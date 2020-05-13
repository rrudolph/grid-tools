import pandas as pd
import arcpy, csv, re

xlsx = r"C:\Temp\SantaCruzIsland_WeedTreatment_20200427\example_form_codes_percents.xlsx"
# fc = r"C:\Temp\Test Domains\CHIS_Rare_Plants_Flattened_20200323_domain_test.gdb\RarePlants_Poly"

update_fc = r"C:\Temp\SantaCruzIsland_WeedTreatment_20200427\NChannelIslandsTreatmentTemplate.gdb\TreatmentFiles\Weed_Point"

def make_code_dict(xlsx, type_):
	xls = pd.ExcelFile(xlsx)
	sheet = xls.sheet_names[0]
	df = xls.parse(sheet).fillna("NoData")
	# df[field].tolist()
	if type_ == "Trade1":
		dict_ = pd.Series(df.Trade1_perc.values,index=df.Form_Code).to_dict()
	elif type_ == "Trade2":
		dict_ = pd.Series(df.Trade2_perc.values,index=df.Form_Code).to_dict()
	return dict_


# codeDict = make_code_dict(xlsx)
trade1 = make_code_dict(xlsx, "Trade1")
trade2 = make_code_dict(xlsx, "Trade2")


# for k, v in trade1.items():
# 	print(k, v)

# for k, v in trade2.items():
# 	print(k, v)

				# 0                     1                   2
fields = ['formulation_Code', 'finished_Gallons', 'finished_Ounces']

print("Entering update cursor")
with arcpy.da.UpdateCursor(update_fc, fields) as cursor:
	for row in cursor:
		code = row[0]
		print(f"Processing {code}")
		for k, v in trade1.items():
			if k == code:
				row[2] = row[1] * v
				cursor.updateRow(row)


		

