import arcpy, os

root = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427"

scratch_ws = os.path.join(root, "scratch.gdb")

print("Deleting")
arcpy.Delete_management(scratch_ws)

print("Creating")
arcpy.management.CreateFileGDB(root, "scratch", "CURRENT")

print("Done")