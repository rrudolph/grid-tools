import arcpy

def get_unique_values(fc, field):
	# Returns unique values of a field into a sorted list
	with arcpy.da.SearchCursor(fc, [field]) as cursor:
		return sorted({row[0] for row in cursor})



fields = ['formulation_Code']

fc = 'Final_RarePlantsAll_NAD83_Zone11N'

for field in fields:
	print("-"*15 + " Field: " + field + " " + "-"*15)
	vals = get_unique_values(fc, field)
	for val in vals:
		print(val)

	print("\n")

