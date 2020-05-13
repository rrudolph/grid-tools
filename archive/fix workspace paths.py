
import arcpy
mxd = arcpy.mapping.MapDocument("CURRENT")
mxd.findAndReplaceWorkspacePaths(r"C:\Temp\SantaCruzIsland_WeedTreatment_20200427\NChannelIslandsTreatmentTemplate.gdb",
	r"C:\Temp\SantaCruzIsland_WeedTreatment_20200427\CHIS_Invasive_Treatments.gdb")
mxd.saveACopy(r"C:\Temp\SantaCruzIsland_WeedTreatment_20200427\Nad83.mxd")
del mxd

