import  arcpy
import pandas as pd
from icecream import ic
import sys

# Don't edit the live service!  Use a .geodatabase sync copy to do big edits like this.
fc = r"C:\GIS\Projects\CHIS Invasives\Feature Downloads\Features_934F9A1B41764DBEA3936EA38C261124.geodatabase\main.Weed_Point"
# fc = r"C:\GIS\Projects\CHIS Invasives\Feature Downloads\Features_934F9A1B41764DBEA3936EA38C261124.geodatabase\main.Weed_Line"


# Now on OneDrive
xlsx = r"C:\Users\RRudolph\OneDrive - DOI\CHIS Invasives\CHIS_Formulation_Codes.xlsx"

field_list = [
	"formulation_Code",
	"finished_Gallons",
	"finished_Ounces",
	"chemical_1",
	"chemical_1_Trade",
	"chem_1_EPA",
	"chem_1_WetRate",
	"chem_1_DryRate",
	"chem_1_Gallons",
	"chem_1_Density",
	"chem_1_Ounces",
	"chem_1_Pounds",
	"chem_2",
	"chemical_2_Trade",
	"chem_2_EPA",
	"chem_2_WetRate",
	"chem_2_DryRate",
	"chem_2_Gallons",
	"chem_2_Density",
	"chem_2_Ounces",
	"chem_2_Pounds",
	"adjuvant_1_Trade",
	"adjuvant_1_EPA",
	"adjuvant_1_Rate",
	"adjuvant_2_Trade",
	"adjuvant_2_EPA",
	"adjuvant_2_Rate",
	"OBJECTID"
	]

## Functions
def get_unique_fc(fc, field):
	with arcpy.da.SearchCursor(fc, [field]) as cursor:
		return {row[0] for row in cursor}


def get_unique_excel(xlsx):
	xls = pd.ExcelFile(xlsx)
	sheet = xls.sheet_names[0]
	return list(xls.parse(sheet)["formulation_Code"])

def check_mismatch():
	print("Checking for missing form codes")
	fc_vals = get_unique_fc(fc, "formulation_Code")
	excel_vals = get_unique_excel(xlsx)
	# ic(fc_vals)
	# ic(excel_vals)

	for val in fc_vals:
		if val not in excel_vals and val is not None:
			sys.exit(f"Found missing val {val} not in excel list")
	else:
		print("No mismatch found")


def get_form_code_data(xlsx):
	xls = pd.ExcelFile(xlsx)
	sheet = xls.sheet_names[0]
	df = xls.parse(sheet)
	return df

def data_lookup(df, row, column):
	# ic(df)
	# ic(row)
	# ic(column)

	df = df.set_index("formulation_Code", drop = False)
	try:
		val = df.loc[row, column]
		ic(val)
		return val
		
	except:
		print("Lookup error.")
		return None


def calc_oz(wet_rate, finished_Gallons, finished_Ounces):
	ic(finished_Gallons)
	if finished_Gallons:
		return wet_rate*(finished_Gallons*128)
	elif finished_Ounces:
		return wet_rate*finished_Ounces


def calc_lbs(dry_rate, finished_Gallons, finished_Ounces):
	'''Need to figure out how to calculate pounds'''
	pass


## For generating the lookup index for the fields
# for i, field in enumerate(field_list):
# 	print(f"{field} = row[{i}]")

herb_df = get_form_code_data(xlsx)

bad_form_codes = []

check_mismatch()

print("Processing herbicide data...")
with arcpy.da.UpdateCursor(fc, field_list) as cursor:
	for row in cursor:
		oid = row[27]
		print(f"{'-'*29} Processing row {oid}")
		# Read data
		formulation_Code = row[0]
		finished_Gallons = row[1]
		finished_Ounces = row[2]
		
		# Write data (reference)
		chemical_1 = row[3]
		chemical_1_Trade = row[4]
		chem_1_EPA = row[5]
		chem_1_WetRate = row[6]
		chem_1_DryRate = row[7]
		chem_1_Gallons = row[8]
		chem_1_Density = row[9]
		chem_1_Ounces = row[10]
		chem_1_Pounds = row[11]
		chem_2 = row[12]
		chemical_2_Trade = row[13]
		chem_2_EPA = row[14]
		chem_2_WetRate = row[15]
		chem_2_DryRate = row[16]
		chem_2_Gallons = row[17]
		chem_2_Density = row[18]
		chem_2_Ounces = row[19]
		chem_2_Pounds = row[20]
		adjuvant_1_Trade = row[21]
		adjuvant_1_EPA = row[22]
		adjuvant_1_Rate = row[23]
		adjuvant_2_Trade = row[24]
		adjuvant_2_EPA = row[25]
		adjuvant_2_Rate = row[26]

		# Test if form code returns none. Procede with data copy if not.

		# Lookup and copy
		try:
			row[3] = data_lookup(herb_df, formulation_Code, "chemical_1")
			row[4] = data_lookup(herb_df, formulation_Code, "chemical_1_Trade")
			row[5] = data_lookup(herb_df, formulation_Code, "chem_1_EPA")

			row[12] = data_lookup(herb_df, formulation_Code, "chem_2")
			row[13] = data_lookup(herb_df, formulation_Code, "chemical_2_Trade")
			row[14] = data_lookup(herb_df, formulation_Code, "chem_2_EPA")

			chem_1_WetRate = data_lookup(herb_df, formulation_Code, "chem_1_WetRate")
			chem_2_WetRate = data_lookup(herb_df, formulation_Code, "chem_2_WetRate")
			row[6] = chem_1_WetRate
			row[15] = chem_2_WetRate
			
			# Calculations
			ic(formulation_Code)
			ic(chem_1_WetRate)
			ic(finished_Gallons)
			ic(finished_Ounces)
			row[10] = calc_oz(chem_1_WetRate, finished_Gallons, finished_Ounces)
			row[19] = calc_oz(chem_2_WetRate, finished_Gallons, finished_Ounces)
			ic(row[10])
			ic(row[19])
						
			cursor.updateRow(row)
		except:
			print("Error")
			bad_form_codes.append(formulation_Code)

			
print(f"Bad form code list: {set(bad_form_codes)}")

print("Done.")