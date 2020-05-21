import os, arcpy

ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\NChannelIslandsTreatmentTemplate.gdb"

arcpy.env.workspace = os.path.join(ws, "NCI_Grids")

fcs = arcpy.ListFeatureClasses()

def get_value(fc):
	'''
	Returns a more descriptive name for the shapefile
	'''
	switcher = {
	"NCI_Grid_800m"               : "800m",
	"NCI_Grid_400m"               : "400m",
	"NCI_Grid_200m"               : "200m",
	"NCI_Grid_100m"               : "100m",
	"NCI_Grid_50m"                : "50m",
	"NCI_Grid_25m"                : "25m",
	"NCI_Grid_12_5m_SMI"          : "12_5m",
	"NCI_Grid_12_5m_SRI_1"        : "12_5m",
	"NCI_Grid_12_5m_SRI_2"        : "12_5m",
	"NCI_Grid_12_5m_SRI_3"        : "12_5m",
	"NCI_Grid_12_5m_SCI_1"        : "12_5m",
	"NCI_Grid_12_5m_SCI_3"        : "12_5m",
	"NCI_Grid_12_5m_SCI_2"        : "12_5m",
	"NCI_Grid_12_5m_SCI_4"        : "12_5m",
	"NCI_Grid_12_5m_Anacapa"      : "12_5m",
	"NCI_Grid_12_5m_Zones"        : "12_5m"
}
	return switcher.get(fc, "Error") 



def make_dict():
	for fc in fcs:
		print('{:30}: "",'.format('"{}"'.format(fc)))

def add_field(fc, field, fieldLength):
    # Adds a field if it doesn't exists
    fieldNames = [f.name for f in arcpy.ListFields(fc)]
    if field in fieldNames:
        # sys.exit("Field exists! ({})".format(field) +  
        #   " Might want to check on that before you overwrite it.")
        print("Field exists.")
        pass
    else:
        arcpy.AddField_management(fc, field, "TEXT", fieldLength)
        print("Successfully added field: " + field)

# make_dict()

for fc in fcs:
	add_field(fc, "IDPK", 50)
	print("Calculating field for " + fc)
	arcpy.management.CalculateField(fc, "IDPK", f'!PageName! + "_{get_value(fc)}"', "PYTHON3", '', "TEXT")

print("Done")