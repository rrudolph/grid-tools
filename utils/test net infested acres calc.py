import arcpy



def process_nia(fc):
	'''Calculate net infested acres field.'''

	def calc_nia(perc_cover, gia):
		'''Calculate the net infested acres data. 
		If 111 is detected as the percent conver, process it as
		a trace.  Otherwise, convert the whole number to a percent value'''
		if perc_cover > 100:
			print("Found trace")
			return 0.001
		else:
			nia = (perc_cover*.01) * gia
			print(f"Calculating NIA: {nia}")
			
			return nia

	field_list = ["percent_Target", "gross_Acres", "net_Acres", 'OBJECTID', 'Action_Type']
	acceptable_features = ["Weed_Line", "Weed_Point"]
	error_list = []

	print("Updating net infested acres...")
	with arcpy.da.UpdateCursor(fc, field_list) as cursor:
		for row in cursor:
			action_type = row[4]
			oid = row[3]
			percent_Target = row[0]
			gia = row[1]

			if action_type in acceptable_features:		
				print(f"Processing oid: {oid}")

				if percent_Target:
					row[2] = calc_nia(percent_Target, gia)
				else:
					error_list.append(oid)
				cursor.updateRow(row)

	print(f"OIDs with percent cover error: {error_list}")

fc = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch.gdb\All_Features_Merge"

process_nia(fc)