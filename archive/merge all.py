import arcpy
ws = "C:/GIS/Projects/CHIS Invasive GeoDB testing/WildLands_Grid_System_20200427/scratch.gdb"
arcpy.env.workspace = ws

fcs = arcpy.ListFeatureClasses("*_joined")

fieldmappings = arcpy.FieldMappings()
    
for fc in fcs:
	print("Adding fc {} to fieldmappings".format(fc))
	fieldmappings.addTable(fc)

print("Merging")
arcpy.Merge_management(fcs, "Merge_test", fieldmappings)