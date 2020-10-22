import arcpy

ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\Features_54015F3F159F48C6A80F16961D044941.geodatabase"

arcpy.env.workspace = ws

# fcs = arcpy.ListFeatureClasses() 

# for fc in fcs:
# 	print(fc)
# 	baseName = arcpy.Describe(fc).baseName
# 	print(baseName)



if ws.endswith(".geodatabase"):
	ws = ws.replace(".geodatabase", ".gdb")
	print(ws)

