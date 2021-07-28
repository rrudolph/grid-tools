import arcpy
import pandas as pd
from tabulate import tabulate


def diff(li1, li2):
    return list(set(li1) - set(li2)) + list(set(li2) - set(li1))

def get_excel_doms(xlsx):
	xls = pd.ExcelFile(xlsx)
	sheet = xls.sheet_names[0]
	return list(xls.parse(sheet)["formulation_Code"])

def get_agol_doms(db, dom_name):
	domains = arcpy.da.ListDomains(db)
	doms = []
	for domain in domains:
	    if domain.name == dom_name:
		    coded_values = domain.codedValues
		    # print(f"Value count: {len(coded_values)}")
		    for val, desc in coded_values.items():
		        # print('{0}'.format(val))
		        doms.append(val)
	return doms

#--------- Run it.

db ="https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Features/FeatureServer"
xlsx = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\grid-tools\CHIS_Formulation_Codes_6-9-21.xlsx"

# agol_dom = 'Weed_Point_formulation_Code_a3bf946ca94440d7b0a3f1299085b7f4'
agol_dom = 'DOM_FormCode'

xlsx_domains = sorted(get_excel_doms(xlsx))
agol_domains = get_agol_doms(db, agol_dom)

for x in xlsx_domains:
	for a in agol_domains:
		if x == a :
			print(f"[+] {x} == {a}")
			break
	else:
		print(f"[-] {x}")

print("---------- Difference list -------------")
print(diff(agol_domains, xlsx_domains))

print("---------- Set Difference list -------------")
xlsx_domains_set = set(xlsx_domains)
agol_domains_set = set(agol_domains)
diff_list = xlsx_domains_set.difference(agol_domains_set)

for d in diff_list:
	print(d)


# table_dict = {}
# table_dict['EXCEL']  = sorted(xlsx_domains)
# table_dict['AGOL']  = sorted(agol_domains)
# print(tabulate(table_dict, headers="keys"))