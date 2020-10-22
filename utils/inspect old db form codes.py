import arcpy, csv
outCSV = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\form codes from old db.csv"

fc = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\CHIS AGOL\7edc8b624ba049cda1b49ffe3e62273b.gdb\ManagementActions"

fields = ['Trade1', 'Trade1Con', 'Trade2', 'Trade2Con']


def get_unique_values(fc, fields):
    # Returns unique values of a field into a sorted list
    with arcpy.da.SearchCursor(fc, fields) as cursor:
        return {(row[0], row[1], row[2], row[3]) for row in cursor}


vals = get_unique_values(fc, fields)

with open(outCSV, "w", newline='') as f:
	w = csv.writer(f)
	w.writerow(['Trade1', 'Trade1Concentration', 'Trade2', 'Trade2Concentration'])

	for val in vals:
		val_list = list(val)
		data = [val_list[0], val_list[1], val_list[2], val_list[3]]
		print(data)
		w.writerow(data)



