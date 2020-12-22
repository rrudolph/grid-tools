import arcpy

def get_unique_values(fc, field):
    # Returns unique values of a field into a sorted list
    with arcpy.da.SearchCursor(fc, [field]) as cursor:
        return {row[0] for row in cursor}

orig_grid = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\Original DB\NChannelIslandsTreatmentTemplate.gdb\NCI_Grids\NCI_Grid_25m"
sbi_grid = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\SBI_Grid.gdb\NCI_Grid_25m_with_SBI_2_sbi_only4"

orig_vals = get_unique_values(orig_grid, "PageName")
sbi_vals = get_unique_values(sbi_grid, "PageName")

# print(orig_vals)
# print(sbi_vals)

for val in sbi_vals:
	if val in orig_vals:
		print(f"{val} repeats")