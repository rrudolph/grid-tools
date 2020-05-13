import arcpy, os

# Functions
def make_mem_name(fc):
	name = arcpy.Describe(fc).name
	return r"in_memory\{}".format(name)

def spatial_ref(fc):
	return arcpy.Describe(fc).spatialReference

def get_geom(fc):
    # Returns a list of geometry from input fc.
    fieldNames = [f.name for f in arcpy.ListFields(fc)]
    geom = []
    with arcpy.da.SearchCursor(fc, ["SHAPE@", input_id]) as cursor:
        for row in cursor:
            geom_field = row[0]  
            id_field = row[1]  
            # print("Getting geometry: Row ID {0}".format(str(id_field)))  
            geom.append((geom_field, id_field))  
    del cursor  
    return geom


# Input vars
inGrid = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\NChannelIslandsTreatmentTemplate.gdb\NCI_Grids\NCI_Grid_25m"
weedPt = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\NChannelIslandsTreatmentTemplate.gdb\TreatmentFiles\Weed_Point"
weedLn = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\NChannelIslandsTreatmentTemplate.gdb\TreatmentFiles\Weed_Line"

# Output vars
outMerge = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch.gdb\spatial_join_merge"
pt_mem = make_mem_name(weedPt)
ln_mem = make_mem_name(weedLn)

# Field mappings
fieldmappings = arcpy.FieldMappings()
fieldmappings.addTable(inGrid)
fieldmappings.addTable(weedPt)
fieldmappings.addTable(weedLn)

# For cutting
cutter = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\NChannelIslandsTreatmentTemplate.gdb\TreatmentFiles\Cut_Line "
out_fc = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch.gdb\spatial_join_merge_cut"


# Point
print("Spatial join for " + pt_mem)
arcpy.SpatialJoin_analysis(target_features=inGrid, 
	join_features=weedPt, 
	out_feature_class=pt_mem, 
	join_operation="JOIN_ONE_TO_ONE", 
	join_type="KEEP_COMMON", 
	field_mapping= fieldmappings,
 	match_option="INTERSECT", 
 	search_radius="", 
 	distance_field_name="")


# Line
print("Spatial join for " + ln_mem)
arcpy.SpatialJoin_analysis(target_features=inGrid,
	join_features=weedLn,
	out_feature_class=ln_mem,
	join_operation="JOIN_ONE_TO_ONE",
	join_type="KEEP_COMMON",
	field_mapping=fieldmappings,
	match_option="INTERSECT",
	search_radius="",
	distance_field_name="")


print("Merging")
arcpy.Merge_management(inputs=[pt_mem, ln_mem], 
	output=outMerge, 
	field_mappings=fieldmappings)

# print("Cutting output")
# slices = []
# print("Getting geometry from input")
# polygons = get_geom(outMerge)
# lines = get_geom(cutter)

# for eachpoly, eachpolyid in polygons:
#     for eachline, eachlineid in lines:
#         if eachline.crosses(eachpoly):
#             try:
#                 # print("{} crosses {}".format(eachlineid, eachpolyid))
#                 slice1, slice2 = eachpoly.cut(eachline)  
#                 slices.insert(0, (slice1, eachpolyid, "Cut"))  
#                 slices.insert(0, (slice2, eachpolyid, "Cut"))
#             except:
#                 # print("Error")
#                 slices.insert(0, (eachpoly, eachpolyid, "Error"))  

# print("Creating output feature class")
# arcpy.CreateFeatureclass_management(os.path.dirname(out_fc),
#     os.path.basename(out_fc), 
#     "POLYGON", 
#     spatial_reference = spatial_ref(outMerge))

# print("Adding Source ID field")
# arcpy.AddField_management(out_fc, "SOURCE_ID", "TEXT")  

# print("Adding CutStatus field")
# arcpy.AddField_management(out_fc, "CutStatus", "TEXT")  

# print("Running insert cursor on new featureclass")
# with arcpy.da.InsertCursor(out_fc, ["SHAPE@", "SOURCE_ID", "CutStatus"]) as icursor:  
#     for eachslice in slices:  
#         icursor.insertRow(eachslice)  
# del icursor  

# print("Done")