import arcpy, os, re, itertools
from functions import *

data_ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\NChannelIslandsTreatmentTemplate.gdb"
scratch_ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch.gdb"
arcpy.env.workspace = scratch_ws


inGrid = os.path.join(data_ws, "NCI_Grids", "NCI_Grid_25m")
cutter = os.path.join(data_ws, "TreatmentFiles", "Cut_Line" )
final_fc = "Merge_Test"
input_id = "PageName"


fc_list = [
	[os.path.join(data_ws, "TreatmentFiles", "Weed_Point"), 'weed_Target'],
	[os.path.join(data_ws, "TreatmentFiles", "Weed_Line"), 'weed_Target'],
	[os.path.join(data_ws, "TreatmentFiles", "No_Target_Point"), "Species1"],
	[os.path.join(data_ws, "TreatmentFiles", "No_Target_Line"), "Species1"],
	[os.path.join(data_ws, "TreatmentFiles", "No_Treatment_Point"), "Species1"],
	[os.path.join(data_ws, "TreatmentFiles", "No_Treatment_Line"), "Species1"]
	]

grid_mem = make_mem_name(inGrid)

Print("Making feature layer")
arcpy.MakeFeatureLayer_management(inGrid, grid_mem) 

spatialref = arcpy.Describe(inGrid).spatialReference


for list_ in fc_list:
	fc = list_[0]
	field = list_[1]
	Print("Running " + fc, "red")
	species_list = get_unique_values(fc, field)
	fc_name = get_base_name(fc)
	for spp in species_list:
		spp_ = re.sub('[^0-9a-zA-Z]+', '_', spp)
		mem_name = "in_memory\\{}_{}".format(fc_name, spp_)
		out_select_by_loc = "Select_{}_{}".format(fc_name, spp_)
		exp = "{} = '{}'".format(field, spp)

		cut_fc = os.path.join(scratch_ws, fc_name + "_grid_cut_" + spp_)
		no_cross_fc = os.path.join(scratch_ws, fc_name +"_no_cross_" +  spp_)

		Print("Selecting {}".format(mem_name), "yellow")
		arcpy.Select_analysis(in_features=fc,
			out_feature_class=mem_name, 
			where_clause=exp)

		Print("Selecting by location for {}".format(mem_name))
		arcpy.SelectLayerByLocation_management(grid_mem, 'intersect', mem_name)

		Print("Copying fc")
		arcpy.CopyFeatures_management(grid_mem, out_select_by_loc)

		lines = get_geom(cutter, input_id)
		polygons = get_geom(out_select_by_loc, input_id)

		slices, no_cross = cut(lines, polygons)

		generate_output_grid(cut_fc, slices, fc, spatialref)
		generate_output_grid(no_cross_fc, no_cross, fc, spatialref)


Print("Merging all joined features", "green")
fcs = arcpy.ListFeatureClasses("*_joined")
fieldmappings = arcpy.FieldMappings()
for fc in fcs:
	Print("Adding fc {} to fieldmappings".format(fc))
	fieldmappings.addTable(fc)

Print("Merging", "green")
arcpy.Merge_management(fcs, final_fc, fieldmappings)

# Check for overlaps
with arcpy.da.SearchCursor(final_fc, ['OID@', 'SHAPE@']) as cur:
	for e1,e2 in itertools.combinations(cur, 2):
		if e1[1].equals(e2[1]):
			msg = '{} overlaps {}'.format(e1[0],e2[0])
			Print(msg, "yellow")
			calc_error_field(final_fc, msg, e2[0])

Print("Done!", "green")