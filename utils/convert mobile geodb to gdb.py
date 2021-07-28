import arcpy
import os

ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\Features_31D94B83B6FD4208BE553821D3178FA8.geodatabase"

out_ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch.gdb"

def convert_mobile_gdb(in_ws, out_ws):

	with arcpy.EnvManager(workspace=in_ws):
	    fcs = arcpy.ListFeatureClasses()
	    for fc in fcs:
	    	new_fc = fc.replace("main.", "")
	    	print(fc, new_fc)
	    	out_fc = os.path.join(out_ws, new_fc)
	    	print(f"Copying to {out_fc}")
	    	arcpy.management.CopyFeatures(fc, out_fc, '', None, None, None)

convert_mobile_gdb(ws, out_ws)