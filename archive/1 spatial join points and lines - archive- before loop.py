import arcpy, os
from collections import Counter

arcpy.env.workspace = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch.gdb"
arcpy.env.overwriteOutput = True
data_ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\NChannelIslandsTreatmentTemplate.gdb\TreatmentFiles" + os.sep

# Functions
def make_mem_name(fc):
	name = arcpy.Describe(fc).name
	return r"in_memory\{}".format(name)

def get_baseName(fc):
	baseName = arcpy.Describe(fc).baseName
	return baseName

def get_all_values(fc, field):
	# Returns unique values of a field into a sorted list
	print("Getting unique values")
	with arcpy.da.SearchCursor(fc, [field]) as cursor:
		return [row[0] for row in cursor]

def cell_count_check(fc, fieldName):
	# There should only be one of each cell. If there are more, that
	# means there are overlapping treatment lines or points. Fix it. 
	counter = Counter(get_all_values(fc, fieldName))
	errorList = []
	for key, count in counter.items():
		if count > 1:
			errorList.append((key, count))

	if len(errorList) > 0:
		print(errorList)
		sys.exit("[-] ERROR! Found overlapping point/line features\n \
			Check for errors in the above cells and try again.")
	else:
		print("[+] No duplicate cells found.")

		

### Input vars
# Select from
inGrid = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\NChannelIslandsTreatmentTemplate.gdb\NCI_Grids\NCI_Grid_25m"

# Select by
weedPt = data_ws + "No_Target_Point"
weedLn = data_ws + "No_Target_Line"

# Output vars
outMerge = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch.gdb\spatial_join_merge"
pt_mem = make_mem_name(weedPt)
ln_mem = make_mem_name(weedLn)
grid_mem = make_mem_name(inGrid)

print("Making feature layer")
arcpy.MakeFeatureLayer_management(inGrid, grid_mem) 

print("Selecting " + get_baseName(weedPt))
arcpy.SelectLayerByLocation_management(grid_mem, 'intersect', weedPt)
print("Copying to " + pt_mem)
arcpy.CopyFeatures_management(grid_mem, pt_mem)

print("Selecting " + get_baseName(weedLn))
arcpy.SelectLayerByLocation_management(grid_mem, 'intersect', weedLn)
print("Copying to " + ln_mem)
arcpy.CopyFeatures_management(grid_mem, ln_mem)

# # Field mappings
fieldmappings = arcpy.FieldMappings()
fieldmappings.addTable(pt_mem)
fieldmappings.addTable(ln_mem)

tempMerge = r"in_memory\tempMerge"
print("Merging to " + tempMerge)
arcpy.Merge_management(inputs=[pt_mem, ln_mem], 
	output=tempMerge, 
	field_mappings=fieldmappings)

fieldmappings.addTable(tempMerge)
fieldmappings.addTable(weedPt)
fieldmappings.addTable(weedLn)

print("Spatial Joining " + get_baseName(weedPt))
arcpy.SpatialJoin_analysis(target_features=tempMerge, 
	join_features=weedPt, 
	out_feature_class=pt_mem,
	join_operation="JOIN_ONE_TO_ONE",
	join_type="KEEP_COMMON", 
	field_mapping=fieldmappings,
	match_option="INTERSECT", 
	search_radius="", 
	distance_field_name="")

print("Spatial Joining " + get_baseName(weedLn))
arcpy.SpatialJoin_analysis(target_features=tempMerge, 
	join_features=weedLn, 
	out_feature_class=ln_mem,
	join_operation="JOIN_ONE_TO_ONE",
	join_type="KEEP_COMMON", 
	field_mapping=fieldmappings,
	match_option="INTERSECT", 
	search_radius="", 
	distance_field_name="")

del fieldmappings
fieldmappings = arcpy.FieldMappings()
fieldmappings.addTable(pt_mem)
fieldmappings.addTable(ln_mem)

print("Final Merging")
arcpy.Merge_management(inputs=[pt_mem, ln_mem], 
	output=outMerge, 
	field_mappings=fieldmappings)

# Run error check on the merged fc.
cell_count_check(outMerge, "PageName")

print("Script successfully completed")