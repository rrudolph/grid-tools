'''
For manually updating the formulation codes directly in AGOL.

See https://support.esri.com/en/technical-article/000014561

'''
import arcpy
import pandas as pd



xlsx = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\grid-tools\CHIS_Formulation_Codes_6-9-21.xlsx"

          # {
          #   "name" : "Aminopyralid 1 (Milestone 7oz/100gal) Agri-Dex 1%_NoWet", 
          #   "code" : "Aminopyralid 1 (Milestone 7oz/100gal) Agri-Dex 1%_NoWet"
          # }, 


xls = pd.ExcelFile(xlsx)
sheet = xls.sheet_names[0]
df = xls.parse(sheet)["formulation_Code"]
xlsx_domains = sorted(list(df))

for x in xlsx_domains:
	print(f"""
          {{
            "name" : "{x}", 
            "code" : "{x}"
          }},""")
