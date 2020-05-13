'''
Not sure why the field mappings aren't working. No clue, but they map all wrong.
'''
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

def select_and_make_temp_list(fc_list, grid):

	return_fc_list = []
	grid_mem = make_mem_name(grid)

	print("Making feature layer")
	arcpy.MakeFeatureLayer_management(grid, grid_mem) 

	for fc in fc_list:
		mem_fc = make_mem_name(fc)
	
		print("Selecting " + get_baseName(fc))
		arcpy.SelectLayerByLocation_management(grid_mem, 'intersect', fc)
		print("Copying to " + mem_fc)
		arcpy.CopyFeatures_management(grid_mem, mem_fc)
		return_fc_list.append(mem_fc)
		

	return return_fc_list

def make_field_mappings(fc_list):
	fieldmappings = arcpy.FieldMappings()
	for fc in fc_list:
		fieldmappings.addTable(fc)
	return fieldmappings

def spatial_join(fc_list, tempMerge, fieldmappings):

	return_fc_list = []
	for fc in fc_list:
		scratch_name = arcpy.CreateScratchName("temp_join_" + get_baseName(fc),
                                       data_type="FeatureClass")
		print("Spatial Joining " + scratch_name)
		arcpy.SpatialJoin_analysis(target_features=tempMerge, 
			join_features=fc, 
			out_feature_class=scratch_name,
			join_operation="JOIN_ONE_TO_ONE",
			join_type="KEEP_COMMON", 
			field_mapping=fieldmappings,
			match_option="INTERSECT", 
			search_radius="", 
			distance_field_name="")

		return_fc_list.append(scratch_name)

	return return_fc_list


### Input vars
# Select from
inGrid = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\NChannelIslandsTreatmentTemplate.gdb\NCI_Grids\NCI_Grid_25m"


# Output vars
outMerge = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch.gdb\spatial_join_merge"

# Select by

fc_dict = {
"Treat": [data_ws + "Weed_Point", data_ws + "Weed_Line"],
"No_Target": [data_ws + "No_Target_Point", data_ws + "No_Target_Line"],
"No_Treatment":[data_ws + "No_Treatment_Point", data_ws + "No_Treatment_Line"]
}

for join_type, fc_list in fc_dict.items():

	temp_list = select_and_make_temp_list(fc_list, inGrid)
	temp_field_mappings = make_field_mappings(fc_list + [inGrid])

	# tempMerge = r"in_memory\tempMerge"
	# tempMerge = "tempMerge"
	tempMerge = arcpy.CreateScratchName("temp_merge_" + join_type,
                                       data_type="FeatureClass")

	print("Merging to " + tempMerge)
	arcpy.Merge_management(inputs=temp_list, 
		output=tempMerge, 
		field_mappings=temp_field_mappings)

	final_merge_list = spatial_join(fc_list, tempMerge, temp_field_mappings)

	final_field_mappings = make_field_mappings(final_merge_list)

	out_fc = outMerge + join_type

	print("Final Merging")
	arcpy.Merge_management(inputs=final_merge_list, 
		output=out_fc, 
		field_mappings=final_field_mappings)

	# # Run error check on the merged fc.
	cell_count_check(out_fc, "PageName")

	del temp_list, temp_field_mappings, final_merge_list, final_field_mappings

print("Script successfully completed")