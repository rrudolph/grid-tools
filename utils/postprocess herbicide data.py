import  arcpy
import pandas as pd

# fc = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\Features_F400A963108049BC9AF700A5BB26EE9B.gdb\Weed_Line"

# weed point
# fc = "https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Features/FeatureServer/0" 

# weed line
fc = "https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Features/FeatureServer/1" 

xlsx = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\grid-tools\CHIS_Formulation_Codes.xlsx"

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
	"adjuvant_2_Rate"
	]

## Functions
def get_form_code_data(xlsx):
	xls = pd.ExcelFile(xlsx)
	sheet = xls.sheet_names[0]
	df = xls.parse(sheet)
	return df

def data_lookup(df, row, column):
	# print(f"DF: {df}")
	# print(f"row: {row}")
	# print(f"col: {column}")

	df = df.set_index("formulation_Code", drop = False) 
	return df.loc[row, column]


def calc_oz(wet_rate, finished_Gallons, finished_Ounces):
	if finished_Gallons:
		return wet_rate*(finished_Gallons*128)
	elif finished_Ounces:
		return wet_rate*finished_Ounces


def calc_lbs(dry_rate, finished_Gallons, finished_Ounces):
	if finished_Gallons:
		return (dry_rate/16)*(finished_Gallons/100)
	elif finished_Ounces:
		return (dry_rate/16)*((finished_Ounces*128)/100)


## For generating the lookup index for the fields
# for i, field in enumerate(field_list):
# 	print(f"{field} = row[{i}]")

herb_df = get_form_code_data(xlsx)

print("Processing herbicide data...")
with arcpy.da.UpdateCursor(fc, field_list) as cursor:
	for row in cursor:
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

		# Lookup and copy
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
		row[10] = calc_oz(chem_1_WetRate, finished_Gallons, finished_Ounces)
		row[19] = calc_oz(chem_2_WetRate, finished_Gallons, finished_Ounces)
		

		
		cursor.updateRow(row)

print("Done.")