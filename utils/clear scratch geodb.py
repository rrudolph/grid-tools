import arcpy

scratch_ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch.gdb"

print("Deleting")
arcpy.Delete_management(scratch_ws)

print("Creating")
arcpy.management.CreateFileGDB(r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427", "scratch", "CURRENT")

print("Done")