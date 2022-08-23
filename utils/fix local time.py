import arcpy

## To do all the fcs
# ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\Features_B4FACD45B2174ECFBDBF32B44F72EBC4.geodatabase"
# arcpy.env.workspace = ws
# fcs = arcpy.ListFeatureClasses()
# print(fcs)

# To do just a targeted set of fcs
fcs = [
r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch_cies_2021.gdb\All_Features_Merge_2021_01_01",
r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch_cies_2021.gdb\All_Features_Merge_2021_01_01_fire_only",
r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch_cies_2022.gdb\All_Features_Merge_2022_01_01",
r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch_cies_2022.gdb\All_Features_Merge_2022_01_01_fire_only",

]

for fc in fcs:

	print(f"Fixing time for {fc}")
	fields = [field.name for field in arcpy.ListFields(fc)]
	if "Action_Date_Local" in fields:
		print("Has action date")
		arcpy.management.ConvertTimeZone(fc,
		"Action_Date",
		"UTC",
		"Action_Date_Local",
		"Pacific_Standard_Time", 
		"INPUT_NOT_ADJUSTED_FOR_DST",
		"OUTPUT_ADJUSTED_FOR_DST")
	else:
		print("No action date")
