'''
Script for automating Wildlands Conservation Science invasives species data collection system.

Update Jan 2023. I eliminated all the python toolbox functionality because I didn't use it and it added 
unecessary complications and code. Sometimes it would accidentally run and cause Pro to crash.

Author: Rocky Rudolph, GISP, rocky_rudolph@nps.gov
Date 1/19/2023
'''


import arcpy
import re
import itertools
import yaml
from pathlib import Path
from os.path import join, dirname, basename
from collections import Counter
from icecream import ic
from timeit import default_timer as timer
from humanfriendly import format_timespan
import logging
import time
try:
    from colorama import Fore, Back, Style, init
    init()
except:
    pass


# Create and configure logger
LOG_FORMAT = "%(levelname)s %(asctime)s - line %(lineno)d - %(message)s"

now = time.localtime() # get struct_time
year, month, day, hour, minute = now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min

# If file doesn't exist, it will be created.  Append is default.
logging.basicConfig(filename =Path(__file__).parent / f'grid_processing_{year}{month}{day}{hour}{minute}.log',
    level = logging.DEBUG,
    format = LOG_FORMAT)

logger = logging.getLogger()


# Define custom functions

def elapsed_time(start,end):
    '''
    Print the elapsed time of how long something took.
    User will need to specify start and end times in the main script
    for each process needing timing. Use start = timer() and end = timer()
    '''
    print(f"Elapsed time: {format_timespan(end - start)}")

def print_(text, color="black"):
    # Make fancy colored output if using the terminal. 
    logger.info(text)

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
            
def add_fc_name(fc):
    base_name = get_base_name(fc)
    print_("Adding FILESOURCE field and calculating")
    arcpy.AddField_management(fc, "FILESOURCE", "text", "", "", "50")
    arcpy.CalculateField_management(fc, "FILESOURCE", f"'{base_name}'", "PYTHON_9.3", "")


def get_buffered_area(fc):
    '''
    Inputs a featureclass that is a buffered weed line.
    Returns the total area buffered in acres. 
    Used for the part of the script that buffered weed lines along roads and trails.  Data needs to be proportional across the
    grid cells that is intersected by the buffered area for a given ween line treatment. This total buffered area is part of the
    calculation to do that proportional herbicide treatment value. 
    '''
    arcpy.management.CalculateGeometryAttributes(fc, "gross_Acres AREA", '', "ACRES", get_config("out_coor_system"), "SAME_AS_INPUT")
    total_area = []
    fields = ['gross_Acres', 'Action_Type']
    with arcpy.da.SearchCursor(fc, fields) as cursor:
        for row in cursor:
            print(f'{row[0]}, {row[1]}')
            if row[1] in ['Weed_Line']:
                print("Appending to total area list")
                total_area.append(row[0])
    return sum(total_area)

def get_base_name(fc):
    # Return the basename of an fc rather than the entire path.
    baseName = arcpy.Describe(fc).baseName
    return baseName

def get_unique_values(fc, field):
    # Returns unique values of a field into a sorted list
    with arcpy.da.SearchCursor(fc, [field]) as cursor:
        return {row[0] for row in cursor if row[0] is not None}

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


def strip_non_alphanum(string):
    return re.sub('[^0-9a-zA-Z]+', '_', string)

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
            return 0.009
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
    arcpy.CreateFeatureclass_management(dirname(out_fc),
        basename(out_fc), 
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
        join_operation="JOIN_ONE_TO_MANY",
        join_type="KEEP_COMMON", 
        field_mapping=fieldmappings,
        match_option="INTERSECT", 
        search_radius="", 
        distance_field_name="")

    add_fc_name(out_join)

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
                    # print_("{} crosses {}".format(line_id, poly_id))
                    crossed_list.append(poly_id)
                    master_cross_list.append(poly_id)
                    try:
                        slice1, slice2 = poly.cut(line)  
                        slices.insert(0, (slice1, poly_id, "Left Cut"))  
                        slices.insert(0, (slice2, poly_id, "Right Cut"))
                    except:
                        slices.insert(0, (poly, poly_id, "Error"))
                else:
                    # print_("{} DOES NOT cross {}".format(line_id, poly_id))
                    line_count += 1

            if line_count >= len(lines) and poly_id not in crossed_list:
                no_cross.insert(0, (poly, poly_id, "No Cross"))

    print(f"Cross List: {crossed_list}")
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
    dir_name = dirname(gdb)
    return_name = join(dir_name, projected_name)
    print(f"Making new fileGDB: {return_name}")
    arcpy.management.CreateFileGDB(dir_name, projected_name, "CURRENT")
    return return_name

def project_all_fcs(gdb):
    """ 
    Projects all fcs in the input geodatbase into State Plane. 
    """
    print("Projecting all fcs")
    fcs = get_fc_list(gdb)
    proj_gdb = make_projected_gdb(gdb)
    for fc in fcs:
        count = arcpy.GetCount_management(fc)
        if int(count[0]) > 0:
            # If the fc has features, reproject it.
            name = arcpy.Describe(fc).name
            print(f"Projecting {fc}")
            arcpy.management.Project(fc, 
                join(proj_gdb, name),
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


def copy_mobile_to_gdb(in_ws, out_ws):
    with arcpy.EnvManager(workspace=in_ws):
        fcs = arcpy.ListFeatureClasses()
        for fc in fcs:
            new_fc = fc.replace("main.", "")
            print(fc, new_fc)
            out_fc = join(out_ws, new_fc)
            print(f"Copying to {out_fc}")
            arcpy.management.CopyFeatures(fc, out_fc, '', None, None, None)

def convert_to_gdb(ws):
    ws_gdb = ws.replace(".geodatabase", ".gdb")
    ws_gdb_name = ws_gdb.split("\\")[-1]
    dir_name = dirname(ws)
    ic(ws_gdb, dir_name, ws_gdb_name)
    arcpy.management.CreateFileGDB(dir_name, ws_gdb_name, "CURRENT")
    print(f"Converting to {ws_gdb}")
    copy_mobile_to_gdb(ws, ws_gdb)
    converted_gdb = project_all_fcs(ws_gdb) 
    return converted_gdb

def get_config(config_item):
    here = Path(__file__).parent
    with open(here.joinpath("config.yaml")) as f:
        data = yaml.safe_load(f)
        return data.get(config_item)

def main(data_ws, scratch_ws, in_grid, select_date_start = None, select_date_end = None, convert_gdb = True):
    '''
    Run the main program.
    data_ws: the workspace where all the data exists.
    scratch_ws: an empty scratch workspace to put output data.
    in_grid: master reference grid data will be attached to.
    select_date: optional, used to select out only past a certain date if desired.
    '''

    arcpy.env.workspace = scratch_ws
    arcpy.env.overwriteOutput = True

    check_scratch_db()

    if convert_gdb:
        data_ws = convert_to_gdb(data_ws)
    else:
        data_ws = data_ws.replace(".geodatabase", ".gdb")
        print_("Skipping gdb conversion", "yellow")

    cutter = join(data_ws, "Cut_Line" )
    input_id = get_config("idpk_field")

    if select_date_start:
        final_fc = f'{get_config("output_fc_name")}_{strip_non_alphanum(select_date_start)}'
    
    else:
        final_fc = get_config("output_fc_name")


    weed_field_list = get_config("weed_field_list")
    other_field_list = get_config("other_field_list")

    fc_list = [
        [join(data_ws, "Weed_Point"), weed_field_list],
        [join(data_ws, "Weed_Line"), weed_field_list],
        [join(data_ws, "No_Target_Point"), other_field_list],
        [join(data_ws, "No_Target_Line"), other_field_list],
        [join(data_ws, "No_Treatment_Point"), other_field_list],
        [join(data_ws, "No_Treatment_Line"), other_field_list]
        ]

    grid_mem = make_mem_name(in_grid)

    print_("Making feature layer")
    arcpy.MakeFeatureLayer_management(in_grid, grid_mem) 

    spatialref = arcpy.Describe(in_grid).spatialReference


    for list_ in fc_list:
        fc = list_[0]
        fields = list_[1]
        print_("Running " + fc, "red")
        for field in fields:
            species_list = get_unique_values(fc, field)
            print_("Species List for field {}:  {}".format(field, str(species_list)), "green")
            fc_name = get_base_name(fc)
            for spp in species_list:
                # Strip any weird characters from the name
                spp_ = re.sub('[^0-9a-zA-Z]+', '_', spp)
                non_buffered_line_exists = False
                buffered_line_executed = False
                temp_feature = f"{fc_name}_{spp_}_temp_spp_select"
                
                if select_date_start and select_date_end:
                    exp = f"{field} = '{spp}' And Action_Date >= timestamp '{select_date_start} 00:00:00' And Action_Date <= timestamp '{select_date_end} 00:00:00'"
                else:
                    exp = "{} = '{}'".format(field, spp)

                print_("Selecting grid {}".format(temp_feature), "magenta")
                arcpy.Select_analysis(in_features=fc,
                    out_feature_class=temp_feature, 
                    where_clause=exp)

                if fc_name == "Weed_Line":
                    # We need to handle weed lines that have buffer values differently
                    weed_line_to_buffer = temp_feature + "_to_buffer"
                    weed_line_not_buffer = temp_feature + "_not_buffer"

                    # Get lines needing buffer
                    print_("Selecting buffer weed lines")
                    arcpy.analysis.Select(temp_feature,
                        weed_line_to_buffer,
                        "meter_Buffer_Distance > 0")
                    
                    # Get all other non buffer lines
                    print_("Selecting non buffer weed lines")
                    arcpy.analysis.Select(temp_feature,
                        weed_line_not_buffer,
                        "meter_Buffer_Distance < 1")

                    weed_line_to_buffer_count = int(arcpy.GetCount_management(weed_line_to_buffer)[0])
                    weed_line_not_buffer_count = int(arcpy.GetCount_management(weed_line_not_buffer)[0])

                    print_(f"Weed lines to buffer: {weed_line_to_buffer_count} and not buffer: {weed_line_not_buffer_count}")

                    if weed_line_to_buffer_count > 0:
                        with arcpy.da.SearchCursor(weed_line_to_buffer, ["OBJECTID", "Action_Date", "applicator", "weed_Target"] ) as cursor:
                            for row in cursor:
                                oid = row[0]  
                                Action_Date = row[1]
                                applicator = row[2]
                                weed_Target = row[3]

                                out_select = f"{weed_line_to_buffer}_{oid}"
                                out_select_buffer = f"{weed_line_to_buffer}_{oid}_buffer"
                                out_select_union = f"{weed_line_to_buffer}_{oid}_union"

                                out_select_grid_by_loc = f"Select_grid_{fc_name}_{spp_}_{oid}"

                                print_(f"Selecting, buffering, unioning {out_select}")
                                arcpy.analysis.Select(weed_line_to_buffer,
                                    out_select,
                                    f"OBJECTID = {oid}")

                                print_("Selecting by location for {}".format(out_select))
                                arcpy.SelectLayerByLocation_management(grid_mem, 'intersect', out_select)

                                print_("Copying {}".format(fc_name))
                                arcpy.CopyFeatures_management(grid_mem, out_select_grid_by_loc)

                                arcpy.analysis.Buffer(out_select,
                                    out_select_buffer,
                                    "meter_Buffer_Distance", "FULL", "FLAT", "NONE", None, "PLANAR")
                                add_field(out_select_buffer, "Action_Type", 50, "Action Type")
                                print_("Calculating field")
                                arcpy.CalculateField_management(out_select_buffer, "Action_Type", f"'Weed_Line'", "PYTHON_9.3", "")

                                arcpy.analysis.Union([out_select_grid_by_loc, out_select_buffer], 
                                    out_select_union,
                                    "ALL", None, "GAPS")

                                print_("Updating union data")
                                with arcpy.da.UpdateCursor(out_select_union, ["Action_Date", "applicator", "weed_Target","Action_Type" ] ) as upcursor:
                                    for row in upcursor:
                                        row[0] = Action_Date
                                        row[1] = applicator
                                        row[2] = weed_Target
                                        if not row[3]:
                                            row[3] = "No_Target_Line_Buffer"
                                        upcursor.updateRow(row)

                                buffered_area = get_buffered_area(out_select_union)

                                print_("Adding original_finished_ounces/gallons fields")
                                arcpy.management.AddField(out_select_union, "original_finished_ounces", "DOUBLE", None, None, None, "Original Finished Ounces Applied", "NULLABLE", "NON_REQUIRED", '')
                                arcpy.management.AddField(out_select_union, "original_finished_gallons", "DOUBLE", None, None, None, "Original Finished Ounces Applied", "NULLABLE", "NON_REQUIRED", '')

                                #                                                  0                     1                       2                    3                          4               5
                                with arcpy.da.UpdateCursor(out_select_union, ['finished_Ounces', 'finished_Gallons', 'original_finished_ounces', 'original_finished_gallons', 'Action_Type', 'gross_Acres']) as cursor:
                                    for row in cursor:
                                        if row[4] in ['Weed_Line']:
                                            if row[0]:
                                                row[2] = row[0] # Keep a record of the original ounces value
                                                row[0] = (row[5] / buffered_area) * row[0] # get ounces proportional to the area and total applied for the line
                                            if row[1]:
                                                row[3] = row[1] # Keep a record of the original gallons value
                                                row[1] = (row[5] / buffered_area) * row[1]
                                            cursor.updateRow(row)

                        add_fc_name(out_select_union)
                        print_(f"Setting buffer line to true")
                        buffered_line_executed = True

                    if weed_line_not_buffer_count > 0:
                        print_(f"Setting not buffered line to true")
                        non_buffered_line_exists = True


                if fc_name != "Weed_Line" or non_buffered_line_exists:

                    if non_buffered_line_exists:
                        print_("Not buffered exists")
                        print_(weed_line_not_buffer)
                        print_(temp_feature)
                        temp_feature = weed_line_not_buffer
                        print_(temp_feature)

                    out_select_grid_by_loc = f"Select_grid_{fc_name}_{spp_}"

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

                    cut_fc = join(scratch_ws, fc_name + "_grid_cut_" + spp_)
                    no_cross_fc = join(scratch_ws, fc_name +"_no_cross_" +  spp_)

                    generate_output_grid(cut_fc, slices, temp_feature, spatialref, spp)
                    generate_output_grid(no_cross_fc, no_cross, temp_feature, spatialref, spp)

                if buffered_line_executed:
                    print_("Yes buffered line executed")
                    pass

    print_("Removing grid_mem var")
    arcpy.Delete_management(grid_mem)

    print_("Merging all joined features", "green")
    fcs = arcpy.ListFeatureClasses("*_joined") + arcpy.ListFeatureClasses("*_union")

    print_("Merging", "green")
    arcpy.Merge_management(fcs, final_fc)

    # Check for overlaps
    with arcpy.da.SearchCursor(final_fc, ['OID@', 'SHAPE@']) as cur:
        for e1,e2 in itertools.combinations(cur, 2):
            if e1[1].equals(e2[1]):
                msg = '{} overlaps {}'.format(e1[0],e2[0])
                print_(msg, "yellow")
                calc_error_field(final_fc, msg, e2[0])

    print_("Deleting unneeded fields", "red")
    del_fields = other_field_list + ["Join_Count", "TARGET_FID"] + [f.name for f in arcpy.ListFields(final_fc) if f.name.startswith("FID")] 
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


    print_("Calculating number of crosses on grid cells")
    counter = Counter(master_cross_list)
    print(f"Master cross list count: {counter}")
    add_field(final_fc, "Times_Crossed", 25)
    with arcpy.da.UpdateCursor(final_fc, ["SOURCE_ID", "Times_Crossed"]) as cursor:

        for row in cursor:
            for id_, count in counter.items():
                if row[0] == id_:
                    print_(f"Found match: {row[0]}")

                    row[1] = count
                    cursor.updateRow(row)

    print_("Combining finished applied ounces and gallons into one field")
    arcpy.AddField_management(final_fc, "finished_Gallons_Total", "DOUBLE", None, None, None, "Finished Gallons Applied Total")
    # The field user can enter in finished applied oz or gallons out of convenience. Combine them into a single field
    # so totals can be calculated.
    with arcpy.da.UpdateCursor(final_fc, ["finished_Gallons", "finished_Ounces", "finished_Gallons_Total"]) as cursor:
        for row in cursor:
            gal = row[0]
            oz = row[1]
            if gal:
                row[2] = gal
            if oz:
                row[2] = oz * 0.0078125

            cursor.updateRow(row)

    print_("Done!", "green")

if __name__ == '__main__':

    global master_cross_list
    master_cross_list = []
    main_script = True
    convert_gdb = True
    data_ws = r"C:\GIS\Projects\CHIS Invasives\Feature Downloads\Features_74C570A176A8418C9D1F85852E6EA9BE.geodatabase"
    in_grid = r"C:\GIS\Projects\CHIS Invasives\Original DB\NChannelIslandsTreatmentTemplate.gdb\NCI_Grids\NCI_Grid_25m"
    scratch_ws = r"C:\GIS\Projects\CHIS Invasives\scratch_pups_2022.gdb"

    if not arcpy.Exists(scratch_ws):
        print_(f"Making scratch GeoDB: {scratch_ws}")
        arcpy.management.CreateFileGDB(str(Path(scratch_ws).parent), str(Path(scratch_ws).name), "CURRENT")

    select_date_start = "2022-01-01"
    select_date_end = "2022-12-31"
    # select_date = None

    start = timer()
    main(data_ws, scratch_ws, in_grid, select_date_start, select_date_end, convert_gdb)
    end = timer()
    elapsed_time(start, end)
    
