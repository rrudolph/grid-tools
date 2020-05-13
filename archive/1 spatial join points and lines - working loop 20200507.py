import arcpy, os
from collections import Counter

# Env vars
arcpy.env.workspace = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch.gdb"
arcpy.env.overwriteOutput = True
data_ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\NChannelIslandsTreatmentTemplate.gdb\TreatmentFiles" + os.sep

# Functions
def make_mem_name(fc):
	name = arcpy.Describe(fc).name
	return r"in_memory\{}".format(name)

def get_base_name(fc):
	baseName = arcpy.Describe(fc).baseName
	return baseName

def cell_count_check(fc, fieldName):
	# There should only be one of each cell. If there are more, that
	# means there are overlapping treatment lines or points. Fix it. 
	with arcpy.da.SearchCursor(fc, [fieldName]) as cursor:
		vals = [row[0] for row in cursor]
	counter = Counter(vals)
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
fc_dict = {
	"Treat": [data_ws + "Weed_Point", data_ws + "Weed_Line"],
	"No_Target": [data_ws + "No_Target_Point", data_ws + "No_Target_Line"],
	"No_Treatment":[data_ws + "No_Treatment_Point", data_ws + "No_Treatment_Line"]
	}

# Loop over dictionary to process all three types of data.
for join_type, fc_list in fc_dict.items():
	fc_pt = fc_list[0]
	fc_ln = fc_list[1]

	# Output vars
	outMerge = "spatial_join_merge_" + join_type
	pt_mem = make_mem_name(fc_pt)
	ln_mem = make_mem_name(fc_ln)
	grid_mem = make_mem_name(inGrid)


	print("Making feature layer")
	arcpy.MakeFeatureLayer_management(inGrid, grid_mem) 

	print("Selecting " + get_base_name(fc_pt))
	arcpy.SelectLayerByLocation_management(grid_mem, 'intersect', fc_pt)
	print("Copying to " + pt_mem)
	arcpy.CopyFeatures_management(grid_mem, pt_mem)

	print("Selecting " + get_base_name(fc_ln))
	arcpy.SelectLayerByLocation_management(grid_mem, 'intersect', fc_ln)
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

	fieldmappings = arcpy.FieldMappings()
	fieldmappings.addTable(tempMerge)
	fieldmappings.addTable(fc_pt)
	fieldmappings.addTable(fc_ln)

	print("Spatial Joining " + get_base_name(fc_pt))
	arcpy.SpatialJoin_analysis(target_features=tempMerge, 
		join_features=fc_pt, 
		out_feature_class=pt_mem,
		join_operation="JOIN_ONE_TO_ONE",
		join_type="KEEP_COMMON", 
		field_mapping=fieldmappings,
		match_option="INTERSECT", 
		search_radius="", 
		distance_field_name="")

	print("Spatial Joining " + get_base_name(fc_ln))
	arcpy.SpatialJoin_analysis(target_features=tempMerge, 
		join_features=fc_ln, 
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

	print("Final Merging for " + join_type)
	arcpy.Merge_management(inputs=[pt_mem, ln_mem], 
		output=outMerge, 
		field_mappings=fieldmappings)

	# Run error check on the merged fc.
	cell_count_check(outMerge, "PageName")

	del pt_mem, ln_mem, grid_mem, fieldmappings, tempMerge

print("Script successfully completed")