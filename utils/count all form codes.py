import arcpy
from collections import Counter
from tabulate import tabulate

def get_all_values(fc, field):
    # Returns all values of a field into a  list
    with arcpy.da.SearchCursor(fc, [field]) as cursor:
        return sorted([row[0] for row in cursor if row[0] is not None])

base_url = "https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Features/FeatureServer/"

fc_dict ={
	"weed_point" : f"{base_url}0",
	"weed_line"  : f"{base_url}1"
	}


for fc_name, url in fc_dict.items():
	vals = get_all_values(url, "formulation_Code")
	counter = Counter(vals)
	print(f"----------{fc_name}----------")
	headers = ["Formualation Code", "Count"]
	print(tabulate([(k,v) for k,v in counter.items()], headers = headers))
	print("\n")
