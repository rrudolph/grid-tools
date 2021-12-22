import arcpy
fc = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\Features_931AFC4EE8FE4F50920839F44961ED47.geodatabase\main.Weed_Point"

# base_url = "https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Features/FeatureServer/"

# weed_point 			= f"{base_url}0"
# weed_line 			= f"{base_url}1"

print(f"Fixing time for {fc}")
arcpy.management.ConvertTimeZone(fc,
"Action_Date",
"UTC",
"Action_Date_Local",
"Pacific_Standard_Time", 
"INPUT_NOT_ADJUSTED_FOR_DST",
"OUTPUT_ADJUSTED_FOR_DST")