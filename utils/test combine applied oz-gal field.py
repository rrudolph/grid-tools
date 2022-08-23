import arcpy

final_fc = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch_cies_2022.gdb\All_Features_Merge_2022_01_01_fire_only"

print("Combining finished applied ounces and gallons into one field")
arcpy.AddField_management(final_fc, "finished_Gallons_Total", "DOUBLE", None, None, None, "Finished Gallons Applied Total")
# The field user can enter in finished applied oz or gallons out of convenience. Combine them into a single field
# so totals can be calculated.
with arcpy.da.UpdateCursor(final_fc, ["finished_Gallons", "finished_Ounces", "finished_Gallons_Total", "Action_Type"]) as cursor:
    for row in cursor:
        gal = row[0]
        oz = row[1]
        action = row[3]
        if gal:
            row[2] = gal
        if oz:
            row[2] = oz * 0.0078125

        cursor.updateRow(row)