import arcpy
ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch_cies_2021.gdb"
fc_name = "All_Features_Merge_2021_01_01"
fc = ws + "\\" + fc_name
selecting_fc = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\Reference_Data.gdb\Scorpion_fire_general_polygon"

print("Selcting")
selected = arcpy.management.SelectLayerByLocation(fc, "INTERSECT", selecting_fc, None, "NEW_SELECTION", "NOT_INVERT")
print("Copying to new fc ")
arcpy.conversion.FeatureClassToFeatureClass(selected, ws, f"{fc_name}_fire_only")