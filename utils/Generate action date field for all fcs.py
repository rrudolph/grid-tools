import os, arcpy

ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\NChannelIslandsTreatmentTemplate.gdb"

arcpy.env.workspace = os.path.join(ws, "TreatmentFiles")

fcs = arcpy.ListFeatureClasses()

def add_date_field(fc, field, alias):
	# Adds a field if it doesn't exists
	fieldNames = [f.name for f in arcpy.ListFields(fc)]
	if field in fieldNames:
		print("Field exists.")
		pass
	else:

		arcpy.AddField_management(in_table=fc,
			field_name=field,
			field_type="DATE",
			field_precision="",
			field_scale="",
			field_length="",
			field_alias=alias,
			field_is_nullable="NULLABLE",
			field_is_required="REQUIRED",
			field_domain="")
		print("Successfully added date field: " + field)

def add_text_field(fc, field, alias):
	# Adds a field if it doesn't exists
	fieldNames = [f.name for f in arcpy.ListFields(fc)]
	if field in fieldNames:
		print("Field exists.")
		pass
	else:

		arcpy.AddField_management(in_table=fc,
			field_name=field,
			field_type="TEXT",
			field_precision="",
			field_scale="",
			field_length="20",
			field_alias=alias,
			field_is_nullable="NULLABLE",
			field_is_required="REQUIRED",
			field_domain="")
		print("Successfully added text field: " + field)



def remove_old_date(fc, field):
	fieldNames = [f.name for f in arcpy.ListFields(fc)]
	if field in fieldNames:
		print("Removing date field")
		arcpy.DeleteField_management(in_table=fc, drop_field=field)
	else:
		print("Date field does not exist, skipping")


for fc in fcs:
	print(fc)
	# remove_old_date(fc, "Action_Date")
	# add_date_field(fc, "Action_Date_UTC", "Action Date UTC")
	add_date_field(fc, "Action_Date_Local", "Action Date Local")



print("Done")