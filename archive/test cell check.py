import arcpy, itertools



def add_field(fc, field):
	# Adds a field if it doesn't exists
	fieldNames = [f.name for f in arcpy.ListFields(fc)]
	if field in fieldNames:
		# sys.exit("Field exists! ({})".format(field) +  
		# 	" Might want to check on that before you overwrite it.")
		print("Field exists.")
		pass
	else:
		arcpy.AddField_management(fc, field, "TEXT", 15)
		print("Successfully added field: " + field)


def calc_error_field(fc, overlapVal, val):
	# Calculates the sub id based on the input val (or key, 
	# or ID, whatever you want to call it)
	with arcpy.da.UpdateCursor(fc, ["OID@", "OverlapError"]) as cursor:

		for row in cursor:
			if row[0] == val:
				print("Found match: " + str(row[0]))

				row[1] = "Yes-{}".format(overlapVal)
				cursor.updateRow(row)



fc = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch.gdb\Merge_test"



with arcpy.da.SearchCursor(fc, ['OID@', 'SHAPE@']) as cur:
	for e1,e2 in itertools.combinations(cur, 2):
		if e1[1].equals(e2[1]):
			add_field(fc, "OverlapError")
			print('{} overlaps {}'.format(e1[0],e2[0]))
			calc_error_field(fc, e1[0], e2[0])

