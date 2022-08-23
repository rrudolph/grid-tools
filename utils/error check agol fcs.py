'''
Checks CHIS AGOL invasive grid features for common errors.
Updated 6/2/2021
R. Rudolph
'''

import arcpy, sys
from icecream import ic
from os.path import join
from tabulate import tabulate


path = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\Feature Downloads\Features_B6972405F82E49F9B4989C7AA8CB3E4F.geodatabase"


weed_point 				= join(path, "main.Weed_Point")
weed_line 				= join(path, "main.Weed_Line")
bread_crumb_point 		= join(path, "main.Bread_Crumb_Point")
bread_crumb_line 		= join(path, "main.Bread_Crumb_Line")
no_target_point			= join(path, "main.No_Target_Point")
no_target_line			= join(path, "main.No_Target_Line")
no_treatment_point		= join(path, "main.No_Treatment_Point")
no_treatment_line		= join(path, "main.No_Treatment_Line")
cut_line				= join(path, "main.Cut_Line")
assignment_point		= join(path, "main.Assignment_Point")
assignment_line			= join(path, "main.Assignment_Line")
correction_needed		= join(path, "main.Correction_Needed")
hidden_weed_point		= join(path, "main.Hidden_Weed_Point")
note 					= join(path, "main.Note")


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
	fields = ["OBJECTID", "finished_Gallons", "finished_Ounces", "formulation_Code", "weed_Target", "treatment_Mode", "percent_Target", "Action_Date", "applicator"]
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
			applicator = row[8]

			error = f"Gallons: ({finished_Gallons}) Ounces: ({finished_Ounces})"
			if finished_Gallons and finished_Ounces:
				error_list.append((oid, action_date, applicator, f"Both have data. {error}"))
			if not finished_Gallons and not finished_Ounces and not is_non_herbicide_mode(treatment_Mode):
				error_list.append((oid, action_date, applicator, f"Neither have data. {error}"))
			if not formulation_Code and not is_non_herbicide_mode(treatment_Mode):
				error_list.append((oid, action_date, applicator, f"Formulation code missing for treatment mode: {treatment_Mode}."))
			if not treatment_Mode or treatment_Mode.isspace():
				error_list.append((oid, action_date, applicator, f"Treatment mode missing: {treatment_Mode}."))
			if not weed_Target or weed_Target.isspace():
				error_list.append((oid, action_date, applicator, "Species name missing."))
			if not percent_Target:
				error_list.append((oid, action_date, applicator, "Percent cover missing."))
			if not action_date:
				error_list.append((oid, action_date, applicator, "UTC date missing."))

	if error_list:
		print(f"Errors detected with weed data")
		error_dict = {}
		error_dict["OIDs"] = map(lambda d: d[0], error_list)
		error_dict["Date (UTC)"] = map(lambda d: d[1], error_list)
		error_dict["Applicator"] = map(lambda d: d[2], error_list)
		error_dict["Message"] = map(lambda d: d[3], error_list)
		print(tabulate(error_dict, headers="keys")) #  tablefmt="grid"
		# for oid, date_, msg in error_list:
		# 	print(f"OID:{oid}, {date_}, {msg}")
		print(f"OIDs: {set([oid for oid, date_, applicator, msg in error_list])}")
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