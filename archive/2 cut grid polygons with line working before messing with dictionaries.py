""" 
Author: Rocky Rudolph, NPS
Date: 2/6/2020
This script was modified from the original source from __author__ = "John K. Tran, Tristan Forward"  
https://community.esri.com/thread/181151

Cut polygons by polylines, splitting each polygon into slices. 
:param to_cut: The polygon to cut. 
:param cutter: The polylines that will each polygon. 
:param out_fc: The output with the split geometry added to it. 

"""  
print("Loading modules...")  
  
import os  
import sys  
import arcpy  

def make_mem_name(fc):
    name = arcpy.Describe(fc).name
    return r"in_memory\{}".format(name)


ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch.gdb"
arcpy.env.workspace = ws
arcpy.env.overwriteOutput = True

to_cut = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch.gdb\spatial_join_merge"
cutter = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\NChannelIslandsTreatmentTemplate.gdb\TreatmentFiles\Cut_Line" 
finalFC = "C:/GIS/Projects/CHIS Invasive GeoDB testing/WildLands_Grid_System_20200427/scratch.gdb/FinalMerge"
out_fc = ws + os.sep + "grid_cut" 
no_cross_fc = ws + os.sep + "no_cross" 
input_id = "PageName"

spatialref = arcpy.Describe(to_cut).spatialReference

def get_geom(fc):
    # Returns a list of geometry from input fc.
    global input_id

    fieldNames = [f.name for f in arcpy.ListFields(fc)]
    if input_id in fieldNames:
        pass
    else:
        input_id = "OID@"

    geom = []
    with arcpy.da.SearchCursor(fc, ["SHAPE@", input_id]) as cursor:
        for row in cursor:
            geom_field = row[0]  
            id_field = row[1]  
            # print("Getting geometry: Row ID {0}".format(str(id_field)))  
            geom.append((geom_field, id_field))  
    del cursor  
    return geom


def generate_output_grid(out_fc, geom):

    print("Creating output feature class")
    arcpy.CreateFeatureclass_management(os.path.dirname(out_fc),
        os.path.basename(out_fc), 
        "POLYGON", 
        spatial_reference = spatialref)

    print("Adding Source ID field")
    arcpy.AddField_management(out_fc, "SOURCE_ID", "TEXT")  

    print("Adding CutStatus field")
    arcpy.AddField_management(out_fc, "CutStatus", "TEXT")  

    print("Running insert cursor on new featureclass")
    with arcpy.da.InsertCursor(out_fc, ["SHAPE@", "SOURCE_ID", "CutStatus"]) as icursor:  
        for polygon in geom:  
            # print(polygon)
            icursor.insertRow(polygon)  
    del icursor

    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(to_cut)
    fieldmappings.addTable(out_fc)

    print("Spatial Join")
    arcpy.SpatialJoin_analysis(target_features=out_fc, 
        join_features=to_cut, 
        out_feature_class=out_fc + "_joined",
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_COMMON", 
        field_mapping=fieldmappings,
        match_option="HAVE_THEIR_CENTER_IN", 
        search_radius="", 
        distance_field_name="")


slices = []
no_cross = []
crossed_dict = {}
not_crossed_dict = {}

print("Getting geometry from input")
polygons = get_geom(to_cut)
lines = get_geom(cutter)


for poly, poly_id in polygons:
    for line, line_id in lines:
        if line.crosses(poly):
            crossed_dict[poly_id] = line_id
            try:
                print("{} crosses {}".format(line_id, poly_id))
                slice1, slice2 = poly.cut(line)  
                slices.insert(0, (slice1, poly_id, "Cut"))  
                slices.insert(0, (slice2, poly_id, "Cut"))
            except:
                # print("Error")
                slices.insert(0, (poly, poly_id, "Error"))

        else:
            not_crossed_dict[poly_id] = line_id
            print("{} DOES NOT cross {}".format(line_id, poly_id))
            no_cross.insert(0, (poly, poly_id, "No Cross"))

print("---------------------Crossed dict")
for k,v in crossed_dict.items():
    print(k, v)

print("---------------------Not Crossed dict")
for k,v in not_crossed_dict.items():
    print(k, v)

# generate_output_grid(out_fc, slices)
# generate_output_grid(no_cross_fc, no_cross)

# fieldmappings = arcpy.FieldMappings()
# fieldmappings.addTable(out_fc + "_joined")
# fieldmappings.addTable(no_cross_fc + "_joined")

# print("Merging final FC")
# arcpy.Merge_management(inputs=[out_fc + "_joined", no_cross_fc + "_joined"], 
#     output=finalFC, 
#     field_mappings=fieldmappings)

# print("Done")