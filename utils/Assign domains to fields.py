import os, arcpy
ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\NChannelIslandsTreatmentTemplate.gdb"
# orig_ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\Original DB\NChannelIslandsTreatmentTemplate.gdb"


## Domain names
# Staff
# Mode
# NCI_Species
# Soil_Description
# AGE_CLASS
# Family
# Hab_Qal
# SCI_WeedList
# YesNo
# Form_Code
# Herbicide_TradeName
# Grid_Scale
# Limitations
# Weed_Targets
# Delete
# WeedLine_Buffer_Side
# AppMode
# SurfactantRate
# RubyLakeNWR_HerbFormulations
# RubyLakeNWR_Species_List
# ID_CONFIDE





def field_lookup(fc):
    '''
    Returns the reordered field list by fc name
    '''
    switcher = {
    "Assigned": "Staff",
	"Assigned_By": "Staff",
	"DyneAmic": "SurfactantRate",
	"Entered_By": "Staff",
	"Grounded": "SurfactantRate",
	"Limitations": "Limitations",
	"Observer": "Staff",
	"Photo_Taken": "YesNo",
	"Species": "SCI_WeedList",
	"Species1": "SCI_WeedList",
	"Species2": "SCI_WeedList",
	"Species3": "SCI_WeedList",
	"Species4": "SCI_WeedList",
	"Species5": "SCI_WeedList",
	"Staff": "Staff",
	"applicator": "Staff",
	"asso_Species_1": "NCI_Species",
	"asso_Species_2": "NCI_Species",
	"asso_Species_3": "NCI_Species",
	"asso_Species_4": "NCI_Species",
	"asso_Species_5": "NCI_Species",
	"formulation_Code": "Form_Code",
	"grid_Scale": "Grid_Scale",
	"retreat": "YesNo",
	"road_Sides": "WeedLine_Buffer_Side",
	"treatment_Mode": "AppMode",
	"weed_Target": "SCI_WeedList",

    }
    return switcher.get(fc, False) 


def check_field_in_dict(field):
	return field_lookup(field)

def make_domain_lookup_dict(fieldList):
	for field in fieldList:
		if field[1] == '':
			pass
		else:
			print(f'"{field[0]}": "{field[1]}",')

def get_all_fields_list():
	# Change to the original workspace to get a list of all the assinged domains
	masterList = []
	arcpy.env.workspace = os.path.join(ws, "TreatmentFiles")
	fcs = arcpy.ListFeatureClasses()
	for fc in fcs:
		fieldNames = [(f.name, f.domain) for f in arcpy.ListFields(fc)]
		masterList += fieldNames

	return sorted(set(masterList))

def list_domains():
	domains = arcpy.da.ListDomains(ws)
	for domain in domains:
		print(domain.name)

def get_fc_list():
	arcpy.env.workspace = os.path.join(ws, "TreatmentFiles")
	return arcpy.ListFeatureClasses()

def  remove_all_domains(fcs):
	for fc in fcs:
		print(fc)
		fieldNames = [f.name for f in arcpy.ListFields(fc)]
		for field in fieldNames:
			print(f"Unassigning domain for field {field}")
			try:
				arcpy.RemoveDomainFromField_management(fc, field)
			except:
				pass

# fields = get_all_fields_list()
# make_domain_lookup_dict(fields)

fcs = get_fc_list()

for fc in fcs:
	print(fc)
	fieldNames = [f.name for f in arcpy.ListFields(fc)]
	for field in fieldNames:
		if check_field_in_dict(field):
			print(f"[+] Found field: {field}, assinging dom: {field_lookup(field)}")
			arcpy.AssignDomainToField_management(fc, field, field_lookup(field))



