fcs = [
# 'Weed_Point',
 # 'Weed_Line',
 'Bread_Crumb_Point',
 'Bread_Crumb_Line',
 'No_Target_Point',
 'No_Target_Line',
 'No_Treatment_Point',
 'No_Treatment_Line',
 'Cut_Line',
 'Assignment_Point',
 'Assignment_Line',
 'Correction_Needed',
 'Hidden_Weed_Point',
 'Note']


for fc in fcs:
    print(f"Appending {fc}")
    arcpy.management.Append(f"'C:/GIS/Projects/CHIS Invasive GeoDB testing/WildLands_Grid_System_20200427/Processing test/fc931ed7c38541df94ca7d28a9834ff0.gdb/{fc}'", fc, "NO_TEST")

