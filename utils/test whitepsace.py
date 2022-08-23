string = " "

print(string.isspace())

import arcpy
from pathlib import Path
scratch_ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch_cies_2022.gdb"
parent_dir = str(Path(scratch_ws).parent)
gdb_name = str(Path(scratch_ws).name)

print(parent_dir)
print(gdb_name)
if not arcpy.Exists(scratch_ws):
    print("doesn't exist, making it")
    arcpy.management.CreateFileGDB(parent_dir, gdb_name, "CURRENT")