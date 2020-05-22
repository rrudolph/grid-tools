import pandas as pd
import arcpy, os

rootDir = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427"

xlsx = os.path.join(rootDir, "Domain files", "Domains.xlsx")

ws = os.path.join(rootDir, "NChannelIslandsTreatmentTemplate.gdb")

csv_folder = os.path.join(rootDir, "Domain files", "temp_csv")

xls = pd.ExcelFile(xlsx)
sheets = xls.sheet_names

for sheet in sheets:
	print(sheet)
	df = xls.parse(sheet) 
	outCSV = os.path.join(csv_folder, sheet + ".csv")
	df.to_csv(outCSV, index=False)

	domTable = outCSV
	codeField = "Code"
	descField = "Description"
	dWorkspace = ws
	domName = sheet
	domDesc = sheet
	updateOption = "REPLACE"

	try:
		# # Process: Create a domain from an existing table
		print("Running table to domain tool for " + sheet)
		arcpy.TableToDomain_management(domTable, codeField, descField, dWorkspace, domName, domDesc, updateOption)
	except:
		print(f"{sheet} FAILED.")




