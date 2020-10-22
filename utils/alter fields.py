#Import geoprocessing
import arcpy

#Set local variables
fc = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch.gdb\Weed_Point_test"
field = "chem_2" #short int, non nullable field
new_name = "chemical_2"
new_alias = "Chemical 2"
new_type = "TEXT"
new_length = "200"
new_is_nullable = "NULLABLE"


#Alter the properties of a non nullable, short data type field to become a text field
print("Altering field")
arcpy.AlterField_management(fc, field, new_name, new_alias, new_type, new_length, new_is_nullable)