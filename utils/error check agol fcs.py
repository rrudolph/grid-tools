'''
Checks CHIS AGOL invasive grid features for common errors.
Updated 6/2/2021
R. Rudolph
'''

import arcpy, sys
from icecream import ic

base_url = "https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Features/FeatureServer/"

weed_point 			= f"{base_url}0"
weed_line 			= f"{base_url}1"
bread_crumb_point 	= f"{base_url}2"
bread_crumb_line 	= f"{base_url}3"
no_target_point 	= f"{base_url}4"
no_target_line 		= f"{base_url}5"
no_treatment_point 	= f"{base_url}6"
no_treatment_line 	= f"{base_url}7"
cut_line 			= f"{base_url}8"
assignment_point 	= f"{base_url}9"
assignment_line 	= f"{base_url}10"
correction_needed 	= f"{base_url}11"
hidden_weed_point 	= f"{base_url}12"
note 				= f"{base_url}13"

all_fcs = [weed_point, 
			weed_line, 
			bread_crumb_point, 
			bread_crumb_line, 
			no_target_point, 
			no_target_line, 
			no_treatment_point, 
			no_treatment_line, 
			cut_line, 
			assignment_point, 
			assignment_line, 
			correction_needed , 
			hidden_weed_point, 
			note 
			]

def get_unique_values(fc, field):
    # Returns unique values of a field into a sorted list
    with arcpy.da.SearchCursor(fc, [field]) as cursor:
        return {row[0] for row in cursor}

def generate_local_time(fc_list):
	for fc in fc_list:
		print(f"Fixing time for {fc}")
		arcpy.management.ConvertTimeZone(fc,
		"Action_Date",
		"UTC",
		"Action_Date_Local",
		"Pacific_Standard_Time",
		"INPUT_NOT_ADJUSTED_FOR_DST",
		"OUTPUT_ADJUSTED_FOR_DST")

def is_non_herbicide_mode(treatment_mode):
	'''Determine if the treatment mode is non-herbicide. These treatment modes
	will not have herbicide numbers, so if herbicide numbers are not found for
	these modes, then that is ok. 
	'''
	non_herbicide_modes = [

		'Manual - Cut Stump',
		'Manual - Cut Stump & Solarize',
		'Manual - Dig & Flip',
		'Manual - Girdle',
		'Manual - Hand Halo',
		'Manual - Hoe',
		'Manual - Hula Hoe (Oscillating Hoe)',
		'Manual - Mulch',
		'Manual - Pull/Dig',
		'Manual - Pull/Dig & Bag',
		'Manual - Solarize',
		'Manual - Steam',
		'Manual - Transplant',
		'Manual - Trim',
		'Mechanical - Cut Stump',
		'Mechanical - Cut Stump & Grind',
		'Mechanical - Cut Stump & Solarize',
		'Mechanical - Dig & Flip',
		'Mechanical - Pull/Dig',
		'Mechanical - Foam',
		'Mechanical - Girdle',
		'Mechanical - Masticate',
		'Mechanical - Trim',
		'Mechanical - Grub',
		'Mechanical - Mow/Cut',
		'Mechanical - Recontour']

	found_mode = False
	for mode in non_herbicide_modes:
		if treatment_mode == mode:
			found_mode = True
			break

	return found_mode

def weed_error_check(fc, msg):
	print(f"{'*'*10} Processing {msg}")
	error_list = []
	fields = ["OBJECTID", "finished_Gallons", "finished_Ounces", "formulation_Code", "weed_Target", "treatment_Mode", "percent_Target", "Action_Date"]
	with arcpy.da.SearchCursor(fc, fields) as cursor:
		for row in cursor:
			oid = row[0]
			finished_Gallons = row[1]
			finished_Ounces = row[2]
			formulation_Code = row[3]
			weed_Target = row[4]
			treatment_Mode = row[5]
			percent_Target = row[6]
			action_date = row[7]

			error = f"Gallons: ({finished_Gallons}) Ounces: ({finished_Ounces})"
			if finished_Gallons and finished_Ounces:
				error_list.append((oid, f"Both have data. {error}"))
			if not finished_Gallons and not finished_Ounces and not is_non_herbicide_mode(treatment_Mode):
				error_list.append((oid, f"Neither have data. {error}"))
			if not formulation_Code and not is_non_herbicide_mode(treatment_Mode):
				error_list.append((oid, f"Formulation code missing for treatment mode: {treatment_Mode}."))
			if not weed_Target:
				error_list.append((oid, "Species name missing."))
			if not percent_Target:
				error_list.append((oid, "Percent cover missing."))
			if not action_date:
				error_list.append((oid, "UTC date missing."))

	if error_list:
		print(f"Errors detected with weed data")
		for oid, msg in error_list:
			print(oid, msg)
		print(f"OIDs: {set([oid for oid, msg in error_list])}")
	else:
		print("No herbicide quantity errors detected.")

def no_t_check(fc, msg):
	print(f"{'*'*10} Processing {msg}")
	error_list = []
	fields = ["OBJECTID", "Action_Date", "Entered_By", "Species1"]
	with arcpy.da.SearchCursor(fc, fields) as cursor:
		for row in cursor:
			oid = row[0]
			action_date = row[1]
			staff = row[2]
			spp = row[3]
			# ic(action_date, staff, spp)

			if action_date is None or action_date == ' ':
				error_list.append((oid, "missing action date."))
			if staff is None or staff == ' ':
				error_list.append((oid, "missing staff."))
			if spp is None or spp == ' ':
				error_list.append((oid, "missing species."))
	if error_list:
		print("Errors detected 'T' features")
		for oid, msg in error_list:
			print(oid, msg)
		print(f"OIDs: {set(oid for oid, msg in error_list)}")
	else:
		print("No 'T' errors found")

def cut_line_error_check(fc, msg):
	print(f"{'*'*10} Processing {msg}")
	error_list = []
	fields = ["OBJECTID", "Action_Date", "Staff", "Species"]
	with arcpy.da.SearchCursor(fc, fields) as cursor:
		for row in cursor:
			oid = row[0]
			action_date = row[1]
			staff = row[2]
			spp = row[3]
			if action_date is None:
				error_list.append((oid, "missing action date."))
			if staff is None:
				error_list.append((oid, "missing staff."))
			if spp is None:
				error_list.append((oid, "missing species."))
	if error_list:
		print("Errors detected with cut line")
		for oid, msg in error_list:
			print(oid, msg)
		print(f"OIDs: {set(oid for oid, msg in error_list)}")
	else:
		print("No cut line errors found")




weed_error_check(weed_point, "weed_point")
weed_error_check(weed_line, "weed_line")
cut_line_error_check(cut_line, "cut_line")
no_t_check(no_target_point, "no_target_point")
no_t_check(no_target_line, "no_target_line")
no_t_check(no_treatment_point, "no_treatment_point")
no_t_check(no_treatment_line, "no_treatment_line")

# generate_local_time(all_fcs)