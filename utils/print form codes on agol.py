import arcpy

db ="https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Features/FeatureServer"

domains = arcpy.da.ListDomains(db)
for domain in domains:
	print(f"---- Domain: {domain.name}")
	coded_values = domain.codedValues
	print(f"Values:")
	for val in coded_values:
		print(val)


###### This crashes!
### print("Attempting to update domain")

### arcpy.AddCodedValueToDomain_management(db, "DOM_DataRecorder", "Sam Furmanski", "Sam Furmanski")
### arcpy.AddCodedValueToDomain_management(db, "DOM_DataRecorder", "Thomas Zlatic", "Thomas Zlatic")

### print('Looks like it worked.')