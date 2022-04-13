'''
Search all fields in a feature service for a specific text keyword.
Updated 3/10/2022
R. Rudolph
'''

import arcpy, sys
from icecream import ic
from os.path import join

fc = "https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Features/FeatureServer/2"

keyword = 'spartium'
# keyword = 'cowan'
fields = arcpy.ListFields(fc)

for field in fields:

	if field.type == 'String':
		print("Searching: ", field.name, field.type)
		with arcpy.da.SearchCursor(fc, ["OBJECTID",field.name]) as cursor:
			for row in cursor:
				oid = row[0]
				data = row[1]
				if data:
					if keyword in data.lower():
						print(oid, data.lower())
				