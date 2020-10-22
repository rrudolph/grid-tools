import arcpy

# For each field in the Hospitals feature class, print
#  the field name, type, and length.
fields = arcpy.ListFields(r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch.gdb\Weed_Point_test")

for field in fields:
	# field.name, field.type, field.length
    print(f"{field.name},{field.aliasName}, {field.length} ,{field.isNullable}")