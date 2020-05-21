'''
Arcpy python toolbox (and standalone script) for use in automating
Wildlands Conservation Science invasives species data collection system.

Author: Rocky Rudolph, GISP, rocky_rudolph@nps.gov
Date 5/20/2020
'''


import arcpy, os, re, itertools
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

        params = [param0, param1]
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
        global main_script
        main_script = False
        run(data_ws, scratch_ws)

        return

def run(data_ws, scratch_ws):
    '''
    Run the main program that accepts workspaces.
    data_ws: the workspace where all the data exists.
    scratch_ws: an empty scratch workspace to put output data.
    '''

    arcpy.env.workspace = scratch_ws
    arcpy.env.overwriteOutput = True


    inGrid = os.path.join(data_ws, "NCI_Grids", "NCI_Grid_25m")
    cutter = os.path.join(data_ws, "TreatmentFiles", "Cut_Line" )
    final_fc = "Merge_Test"
    input_id = "IDPK"

    weed_field_list = ["weed_Target"]
    other_field_list = ["Species1", "Species2","Species3","Species4","Species5",]

    fc_list = [
        [os.path.join(data_ws, "TreatmentFiles", "Weed_Point"), weed_field_list],
        [os.path.join(data_ws, "TreatmentFiles", "Weed_Line"), weed_field_list],
        [os.path.join(data_ws, "TreatmentFiles", "No_Target_Point"), other_field_list],
        [os.path.join(data_ws, "TreatmentFiles", "No_Target_Line"), other_field_list],
        [os.path.join(data_ws, "TreatmentFiles", "No_Treatment_Point"), other_field_list],
        [os.path.join(data_ws, "TreatmentFiles", "No_Treatment_Line"), other_field_list]
        ]

    grid_mem = make_mem_name(inGrid)

    print_("Making feature layer")
    arcpy.MakeFeatureLayer_management(inGrid, grid_mem) 

    spatialref = arcpy.Describe(inGrid).spatialReference


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
                    spp_ = re.sub('[^0-9a-zA-Z]+', '_', spp)
                    mem_name = "in_memory\\{}_{}".format(fc_name, spp_)
                    out_select_by_loc = "Select_{}_{}".format(fc_name, spp_)
                    
                    exp = "{} = '{}'".format(field, spp)

                    print_("Selecting {}".format(mem_name), "magenta")
                    arcpy.Select_analysis(in_features=fc,
                        out_feature_class=mem_name, 
                        where_clause=exp)

                    print_("Selecting by location for {}".format(mem_name))
                    arcpy.SelectLayerByLocation_management(grid_mem, 'intersect', mem_name)

                    print_("Copying fc")
                    arcpy.CopyFeatures_management(grid_mem, out_select_by_loc)

                    lines = get_geom(cutter, input_id)
                    polygons = get_geom(out_select_by_loc, input_id)

                    slices, no_cross = cut(lines, polygons)

                    cut_fc = os.path.join(scratch_ws, fc_name + "_grid_cut_" + spp_)
                    no_cross_fc = os.path.join(scratch_ws, fc_name +"_no_cross_" +  spp_)

                    generate_output_grid(cut_fc, slices, fc, spatialref, spp)
                    generate_output_grid(no_cross_fc, no_cross, fc, spatialref, spp)


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

    print_("Done!", "green")

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

def generate_output_grid(out_fc, geom, join_fc, sr, species):
    '''
    Creates a new featureclass based on cut or uncut geometry from the cut function.
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
    arcpy.CalculateField_management(out_join, action_field, "'{}'".format(fieldName), "PYTHON_9.3", "")

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



def stand_alone():
    global main_script
    main_script = True

    data_ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\NChannelIslandsTreatmentTemplate.gdb"
    scratch_ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch.gdb"

    run(data_ws, scratch_ws)

if run_stand_alone:
    stand_alone()