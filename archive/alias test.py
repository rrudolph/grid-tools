import arcpy

fc = r"C:\Temp\SantaCruzIsland_WeedTreatment_20200427\CHIS_Invasive_Treatments.gdb\TreatmentFiles\Weed_Point"



flds_alias = [f.aliasName for f in arcpy.ListFields(fc)]
flds_names = [f.name for f in arcpy.ListFields(fc)]

joined = [' -- '.join(map(str, i)) for i in zip(flds_names, flds_alias)]

fieldsString = ' ; '.join(str(e) for e in joined)

print(fieldsString)