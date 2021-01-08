'''
Arcpy python toolbox (and standalone script) for use in automating
Wildlands Conservation Science invasives species data collection system.

Author: Rocky Rudolph, GISP, rocky_rudolph@nps.gov
Date 5/20/2020
'''


import arcpy, os, re, itertools, yaml
try:
    from colorama import Fore, Back, Style, init
    init()
except:
    pass

# TODO: Add buffer for weed_line, by direction, then spatial interesect the grid 

run_stand_alone = True

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [CutAndMergeCells]


class CutAndMergeCells(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "CutAndMergeCells"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
        displayName="Data Workspace",
        name="data_ws",
        datatype="GPString",
        parameterType="Required",
        direction="Input")

        param1 = arcpy.Parameter(
        displayName="Scratch Workspace",
        name="ws",
        datatype="GPString",
        parameterType="Required",
        direction="Input")

        param2 = arcpy.Parameter(
        displayName="Grid",
        name="in_grid",
        datatype="GPString",
        parameterType="Required",
        direction="Input")


        params = [param0, param1, param2]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        data_ws = parameters[0].valueAsText
        scratch_ws = parameters[1].valueAsText
        in_grid  = parameters[2].valueAsText
        global main_script
        main_script = False
        run(data_ws, scratch_ws, in_grid)

        return


def print_(text, color="black"):
    # Make fancy colored output if using the terminal. 

    if main_script:
        if color == "red":
            try:
                print(Back.RED + text+ Style.RESET_ALL)
            except:
                print(text)
        elif color == "yellow":
            try:
                print(Fore.BLACK + Back.YELLOW + text + Style.RESET_ALL)
            except:
                print(text)

        elif color == "green":
            try:
                print(Fore.BLACK + Back.GREEN + text + Style.RESET_ALL)
            except:
                print(text)

        elif color == "magenta":
            try:
                print(Fore.WHITE + Back.MAGENTA + Style.BRIGHT + text + Style.RESET_ALL)
            except:
                print(text)

        elif color == "cyan":
            try:
                print(Fore.WHITE + Back.CYAN + Style.BRIGHT + text + Style.RESET_ALL)
            except:
                print(text)

        else:
            print(text)
            
    else:
        arcpy.AddMessage(text)

def get_base_name(fc):
    # Return the basename of an fc rather than the entire path.
    baseName = arcpy.Describe(fc).baseName
    return baseName

def get_unique_values(fc, field):
    # Returns unique values of a field into a sorted list
    with arcpy.da.SearchCursor(fc, [field]) as cursor:
        return {row[0] for row in cursor}

def make_mem_name(fc):
    # Make an in-memory temporary featureclass
    name = arcpy.Describe(fc).name
    return r"in_memory\{}".format(name)

def check_field(fc, field):
    # Check if field exists
    fieldNames = [f.name for f in arcpy.ListFields(fc)]
    if field in fieldNames:
        return True
    else:
        return False

def add_field(fc, field, fieldLength, alias = None):
    # Adds a field if it doesn't exists
    fieldNames = [f.name for f in arcpy.ListFields(fc)]
    if field in fieldNames:
        # sys.exit("Field exists! ({})".format(field) +  
        #   " Might want to check on that before you overwrite it.")
        print_("Field exists.")
        pass
    else:
        arcpy.AddField_management(fc, field, "TEXT", fieldLength, field_alias = alias)
        print_("Successfully added field: " + field)

def delete_fields(fc, fieldList):
    '''
    Delete fields. Accepts a featureclass and a list of field names. 
    '''
    for field in fieldList:
        try:
            print_("Deleting field " + field, "yellow")
            arcpy.DeleteField_management(in_table=fc, drop_field=field)
        except:
            print_("Error deleting field " + field, "red")

def calc_error_field(fc, msg, val):
    # Calculates the sub id based on the input val (or key, 
    # or ID, whatever you want to call it)
    error_field_name = "Overlap_Issue"
    add_field(fc, error_field_name, 25)
    with arcpy.da.UpdateCursor(fc, ["OID@", error_field_name]) as cursor:

        for row in cursor:
            if row[0] == val:
                print_("Found match: " + str(row[0]))

                row[1] = msg
                cursor.updateRow(row)



def process_nia(fc):
    '''Calculate net infested acres field.'''

    def calc_nia(perc_cover, gia):
        '''Calculate the net infested acres data. 
        If 111 is detected as the percent conver, process it as
        a trace.  Otherwise, convert the whole number to a percent value'''
        if perc_cover > 100:
            # print("Found trace")
            return 0.001
        else:
            nia = (perc_cover*.01) * gia
            # print(f"Calculating NIA: {nia}")
            return nia

    field_list = ["percent_Target", "gross_Acres", "net_Acres", 'OBJECTID', 'Action_Type']
    acceptable_features = ["Weed_Line", "Weed_Point"]
    error_list = []

    print("Updating net infested acres...")
    with arcpy.da.UpdateCursor(fc, field_list) as cursor:
        for row in cursor:
            action_type = row[4]
            oid = row[3]
            percent_Target = row[0]
            gia = row[1]

            if action_type in acceptable_features:      
                # print(f"Processing oid: {oid}")

                if percent_Target:
                    row[2] = calc_nia(percent_Target, gia)
                else:
                    error_list.append(oid)
                cursor.updateRow(row)

    print(f"OIDs with percent cover error: {error_list}")

def get_geom(fc, inputID):
    # Returns a list of geometry from input fc.
    fieldNames = [f.name for f in arcpy.ListFields(fc)]
    if inputID in fieldNames:
        pass
    else:
        inputID = "OID@"

    geom = []
    print_("Generating geometry feature for " + get_base_name(fc), "yellow")
    with arcpy.da.SearchCursor(fc, ["SHAPE@", inputID]) as cursor:
        for row in cursor:
            geom_field = row[0]  
            id_field = row[1]  
            # print_("Getting geometry: Row ID {0}".format(str(id_field)))  
            geom.append((geom_field, id_field))  
    del cursor  
    return geom


def get_action_type(fc):
    '''The script selects by species name and appends that to the name of
    the temporary in-memory fc.  This function strips the spp name out because
    it is unessesary to put in the action type field. This is used towards the
    end of the generate_output_grid() func. 
    '''
    prefix_list = [
    "No_Target_Line",
    "No_Target_Point",
    "No_Treatment_Line",
    "No_Treatment_Point",
    "Weed_Line",
    "Weed_Point",
    ]

    for prefix in prefix_list:
        if fc.startswith(prefix):
            return "'{}'".format(prefix)

    else:
        return "'{}'".format("Action type error")
    
def generate_output_grid(out_fc, geom, join_fc, sr, species):
    ''' Creates a new featureclass based on cut or uncut geometry from the cut function.
    Does a spatial join from the source point or line feature. Adds needed fields.
    '''
    print_("Generating grid for " + out_fc, "yellow")
    print_("Creating output feature class")
    arcpy.CreateFeatureclass_management(os.path.dirname(out_fc),
        os.path.basename(out_fc), 
        "POLYGON", 
        spatial_reference = sr)

    print_("Adding Source ID field")
    arcpy.AddField_management(out_fc, "SOURCE_ID", "TEXT")  

    print_("Adding CutStatus field")
    arcpy.AddField_management(out_fc, "CutStatus", "TEXT")  

    print_("Running insert cursor on new featureclass")
    with arcpy.da.InsertCursor(out_fc, ["SHAPE@", "SOURCE_ID", "CutStatus"]) as icursor:  
        for polygon in geom:  
            # print_(polygon)
            icursor.insertRow(polygon)  
    del icursor

    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(join_fc)
    fieldmappings.addTable(out_fc)

    out_join = out_fc + "_joined"
    print_("Spatial Join")
    arcpy.SpatialJoin_analysis(target_features=out_fc, 
        join_features=join_fc, 
        out_feature_class=out_join,
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_COMMON", 
        field_mapping=fieldmappings,
        match_option="INTERSECT", 
        search_radius="", 
        distance_field_name="")

    # Add the name of the feature to the attribute table. This will allow the user to see the source of 
    # the feature and its type.
    action_field = "Action_Type"
    print_("Adding and calculating field name: " + action_field)
    fieldName = get_base_name(join_fc)
    add_field(out_join, action_field, 50, "Action Type")
    print_("Calculating field")
    arcpy.CalculateField_management(out_join, action_field, get_action_type(fieldName), "PYTHON_9.3", "")

    # Add weed target field if it doesn't exist. This is for the non-weed treatment features.
    weed_target = "weed_Target"
    if not check_field(out_join, weed_target):
        print("Adding weed {} field".format(weed_target))
        add_field(out_join, weed_target, 100)
        print_("Calculating field")
        arcpy.CalculateField_management(out_join, weed_target, "'{}'".format(species), "PYTHON_9.3", "")



def cut(lines, polygons):
    '''
    Cut a cell by a line. Put into two lists of geometry, cells that got cut,
    and cells that did not get cut.  Return both lists.
    '''
    print_("Cutting", "cyan")
    slices = []
    no_cross = []
    crossed_list = []

    for poly, poly_id in polygons:
            line_count = 0
            for line, line_id in lines:
                if line.crosses(poly):
                    print_("{} crosses {}".format(line_id, poly_id))
                    crossed_list.append(poly_id)
                    try:
                        slice1, slice2 = poly.cut(line)  
                        slices.insert(0, (slice1, poly_id, "Left Cut"))  
                        slices.insert(0, (slice2, poly_id, "Right Cut"))
                    except:
                        slices.insert(0, (poly, poly_id, "Error"))
                else:
                    print_("{} DOES NOT cross {}".format(line_id, poly_id))
                line_count += 1

            if line_count >= len(lines) and poly_id not in crossed_list:
                no_cross.insert(0, (poly, poly_id, "No Cross"))

    return slices, no_cross


def check_scratch_db():
    fcs = arcpy.ListFeatureClasses()
    if len(fcs) > 0:
        sys.exit('''
WARNING!
Your scratch geodatabase is not empty. It is advised to have an empty scratch workspace before proceeding.
Please delete files from it and try again.
''')
    else:
        print_("Scratch workspace empty, continuing...", "green")

def check_spatial_ref(fc):
    """Checks for a specified spatial reference.  Exits if not met. 
    """
    sr_name = arcpy.Describe(fc).spatialReference.name
    alias = arcpy.Describe(fc).spatialReference.alias
    pcs_code = arcpy.Describe(fc).spatialReference.PCSCode
    proj_code = arcpy.Describe(fc).spatialReference.projectionCode
    proj_name = arcpy.Describe(fc).spatialReference.projectionName
     
    if not sr_name == "WGS_1984_Web_Mercator_Auxiliary_Sphere":
        print_(f'''
WARNING!
Featureclass {fc} is not in WGS_1984_Web_Mercator_Auxiliary_Sphere,
sr_name = {sr_name}
alias = {alias}
pcs_code = {pcs_code}
proj_code = {proj_code}
proj_name = {proj_name}
It should be in Web Mercator so it can be properly projected into the standard NAD_1983_StatePlane_California_V_FIPS_0405
used in this project.  
''', "yellow")

    else:
        print_(f"Featureclass {fc} is good: {sr_name}", "green")

def get_fc_list(inWS:"Input workspace") -> "Full list of featureclasses":
    """Temporarily sets the workspace and returns the full path and name of each fc."""
    return_ = []
    with arcpy.EnvManager(workspace=inWS):
        fcs = arcpy.ListFeatureClasses()
        for fc in fcs:
            check_spatial_ref(fc)
            desc = arcpy.Describe(fc)
            catPath = desc.catalogPath
            return_.append(catPath)
    return return_

def make_projected_gdb(gdb):
    """ 
    Makes a geodatabase with the same name but with _projected at the end. 
    Input a path to a geodatabase. 
    """
    gdb_name = arcpy.Describe(gdb).name
    projected_name = gdb_name.split(".")[0] + "_projected." + gdb_name.split(".")[1]
    dir_name = os.path.dirname(gdb)
    return_name = os.path.join(dir_name, projected_name)
    print(f"Making new fileGDB: {return_name}")
    arcpy.management.CreateFileGDB(dir_name, projected_name, "CURRENT")
    return return_name

def project_all_fcs(gdb):
    """ 
    Projects all fcs in the input geodatbase into State Plane. 
    """
    fcs = get_fc_list(gdb)
    proj_gdb = make_projected_gdb(gdb)
    for fc in fcs:
        count = arcpy.GetCount_management(fc)
        if int(count[0]) > 0:
            # If the fc has features, reproject it.
            name = arcpy.Describe(fc).name
            print(f"Projecting {fc}")
            arcpy.management.Project(fc, 
                os.path.join(proj_gdb, name),
                get_config("out_coor_system"),
                get_config("transform_method"),
                get_config("in_coor_system"),
                "NO_PRESERVE_SHAPE",
                None,
                "NO_VERTICAL")


        else:
            # If it doesn't have features, make an empty projected place holder so
            # it doesn't break the script later if it doesn't exist.
            print_(f"Not projecting {fc}, no features present. Making empty fc.", "red")
            name = arcpy.Describe(fc).name
            geometry_type = arcpy.Describe(fc).shapeType
            arcpy.CreateFeatureclass_management(proj_gdb,
                name,
                geometry_type,
                fc,
                "DISABLED",
                "DISABLED",
                get_config("out_coor_system"))

    return proj_gdb


def convert_to_gdb(ws):
    ws_gdb = ws.replace(".geodatabase", ".gdb")
    print(f"Converting to {ws_gdb}")
    arcpy.conversion.MobileGdbToFileGdb(ws, ws_gdb)
    converted_gdb = project_all_fcs(ws_gdb) 
    return converted_gdb


def get_config(config_item):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path,'config.yaml')) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        return data.get(config_item)

def run(data_ws, scratch_ws, in_grid, select_date = None):
    '''
    Run the main program that accepts workspaces.
    data_ws: the workspace where all the data exists.
    scratch_ws: an empty scratch workspace to put output data.
    '''

    arcpy.env.workspace = scratch_ws
    arcpy.env.overwriteOutput = True

    data_ws = convert_to_gdb(data_ws)


    cutter = os.path.join(data_ws, "Cut_Line" )
    final_fc = get_config("output_fc_name")
    input_id = get_config("idpk_field")

    weed_field_list = get_config("weed_field_list")
    other_field_list = get_config("other_field_list")

    fc_list = [
        [os.path.join(data_ws, "Weed_Point"), weed_field_list],
        [os.path.join(data_ws, "Weed_Line"), weed_field_list],
        [os.path.join(data_ws, "No_Target_Point"), other_field_list],
        [os.path.join(data_ws, "No_Target_Line"), other_field_list],
        [os.path.join(data_ws, "No_Treatment_Point"), other_field_list],
        [os.path.join(data_ws, "No_Treatment_Line"), other_field_list]
        ]

    grid_mem = make_mem_name(in_grid)

    print_("Making feature layer")
    arcpy.MakeFeatureLayer_management(in_grid, grid_mem) 

    spatialref = arcpy.Describe(in_grid).spatialReference

    check_scratch_db()

    for list_ in fc_list:
        fc = list_[0]
        fields = list_[1]
        print_("Running " + fc, "red")
        for field in fields:
            species_list = get_unique_values(fc, field)
            print_("Species List for field {}:  {}".format(field, str(species_list)), "green")
            fc_name = get_base_name(fc)
            for spp in species_list:
                if spp:
                    # Strip any weird characters from the name
                    spp_ = re.sub('[^0-9a-zA-Z]+', '_', spp)

                    temp_feature = "in_memory\\{}_{}".format(fc_name, spp_)
                    out_select_grid_by_loc = "Select_grid_{}_{}".format(fc_name, spp_)
                    
                    if select_date:
                        exp = "{} = '{}' And Action_Date >= timestamp '{}'".format(field, spp, select_date)
                    else:
                        exp = "{} = '{}'".format(field, spp)

                    print_("Selecting grid {}".format(temp_feature), "magenta")
                    arcpy.Select_analysis(in_features=fc,
                        out_feature_class=temp_feature, 
                        where_clause=exp)

                    print_("Selecting by location for {}".format(temp_feature))
                    arcpy.SelectLayerByLocation_management(grid_mem, 'intersect', temp_feature)

                    print_("Copying {}".format(fc_name))
                    arcpy.CopyFeatures_management(grid_mem, out_select_grid_by_loc)

                    cutter_select = "Cutter_{}".format(spp_)

                    print_("Selecting cut line to match species {}".format(cutter_select), "magenta")
                    arcpy.Select_analysis(in_features=cutter,
                        out_feature_class=cutter_select, 
                        where_clause="Species = '{}'".format(spp))

                    lines = get_geom(cutter_select, input_id)
                    polygons = get_geom(out_select_grid_by_loc, input_id)

                    slices, no_cross = cut(lines, polygons)

                    cut_fc = os.path.join(scratch_ws, fc_name + "_grid_cut_" + spp_)
                    no_cross_fc = os.path.join(scratch_ws, fc_name +"_no_cross_" +  spp_)

                    generate_output_grid(cut_fc, slices, temp_feature, spatialref, spp)
                    generate_output_grid(no_cross_fc, no_cross, temp_feature, spatialref, spp)

                    print_("Removing temp_feature var")
                    arcpy.Delete_management(temp_feature)

    print_("Removing grid_mem var")
    arcpy.Delete_management(grid_mem)

    print_("Merging all joined features", "green")
    fcs = arcpy.ListFeatureClasses("*_joined")
    fieldmappings = arcpy.FieldMappings()
    for fc in fcs:
        print_("Adding fc {} to fieldmappings".format(fc))
        fieldmappings.addTable(fc)

    print_("Merging", "green")
    arcpy.Merge_management(fcs, final_fc, fieldmappings)

    # Check for overlaps
    with arcpy.da.SearchCursor(final_fc, ['OID@', 'SHAPE@']) as cur:
        for e1,e2 in itertools.combinations(cur, 2):
            if e1[1].equals(e2[1]):
                msg = '{} overlaps {}'.format(e1[0],e2[0])
                print_(msg, "yellow")
                calc_error_field(final_fc, msg, e2[0])

    print_("Deleting unneeded fields", "red")
    del_fields = other_field_list + ["Join_Count", "TARGET_FID"]
    delete_fields(final_fc, del_fields)

    print_("Calculating gross infested acres")
    arcpy.management.CalculateGeometryAttributes(final_fc,
        "gross_Acres AREA_GEODESIC",
        '',
        "ACRES",
        get_config("utm_proj_string"),
        "SAME_AS_INPUT")

    print_("Calculating net infested acres")
    process_nia(final_fc)

    print_("Updating local time field")
    arcpy.management.ConvertTimeZone(final_fc,
        "Action_Date",
        "UTC",
        "Action_Date_Local",
        "Pacific_Standard_Time",
        "INPUT_NOT_ADJUSTED_FOR_DST",
        "OUTPUT_ADJUSTED_FOR_DST")

    print_("Done!", "green")

def stand_alone():
    global main_script
    main_script = True

    data_ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\Features_D27F07CE71AD4AC6AFD09BE4DC3D89D3.geodatabase"
    in_grid = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\Original DB\NChannelIslandsTreatmentTemplate.gdb\NCI_Grids\NCI_Grid_25m"
    scratch_ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch.gdb"

    # select_date = "2020-10-13"
    select_date = None

    run(data_ws, scratch_ws, in_grid, select_date)

if run_stand_alone:
    stand_alone()