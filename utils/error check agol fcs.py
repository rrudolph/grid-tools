import arcpy, sys

weed_point = "https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Features/FeatureServer/0"
weed_line = "https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Features/FeatureServer/1"
no_target_point = "https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Features/FeatureServer/4"
no_target_line = "https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Features/FeatureServer/5"
no_treatment_point = "https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Features/FeatureServer/6"
no_treatment_line = "https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Features/FeatureServer/7"
cut_line = "https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Features/FeatureServer/8"


def weed_error_check(fc):
	print(f"Processing {fc}")
	error_list = []
	with arcpy.da.UpdateCursor(fc, 	["OBJECTID", "finished_Gallons", "finished_Ounces", "formulation_Code"]) as cursor:
		for row in cursor:
			oid = row[0]
			finished_Gallons = row[1]
			finished_Ounces = row[2]
			formulation_Code = row[3]
			error = f"Gallons: ({finished_Gallons}) Ounces: ({finished_Ounces}) at OID: {oid}.  Something is wrong, please check."
			if finished_Gallons and finished_Ounces:
				error_list.append("Both have data. " + error)
			if not finished_Gallons and not finished_Ounces:
				error_list.append("Neither have data. " + error)
			if not formulation_Code:
				error_list.append("Formulation code missing. " + error)
	if error_list:
		print(f"Errors detected with herbicide quantity")
		for error in error_list:
			print(error)
		print("Please check errors and try again")
	else:
		print("No herbicide quantity errors detected.")

def cut_line_error_check(fc):
	print(f"Processing {fc}")
	error_list = []
	with arcpy.da.UpdateCursor(fc, 	["OBJECTID", "Action_Date", "Staff", "Species"]) as cursor:
		for row in cursor:
			oid = row[0]
			action_date = row[1]
			staff = row[2]
			spp = row[3]
			if action_date is None:
				error_list.append(f"OID: {oid} error, missiong action date.")
			if staff is None:
				error_list.append(f"OID: {oid} error, missiong staff.")
			if spp is None:
				error_list.append(f"OID: {oid} error, missiong species.")
	if error_list:
		print("Errors detecte")
		for error in error_list:
			print(error)
	else:
		print("No cut line errors found")


weed_error_check(weed_point)
weed_error_check(weed_line)
cut_line_error_check(cut_line)