import arcpy, os

workspace = r"C:\Temp\SantaCruzIsland_WeedTreatment_20200427\NChannelIslandsTreatmentTemplate.gdb"
outGDB = r"C:\Temp\SantaCruzIsland_WeedTreatment_20200427\CHIS_Invasive_Treatments.gdb"

walk = arcpy.da.Walk(workspace)

def reproject(inFC, outFC):
	print(f"Reprojecting {inFC}, output {outFC}")
	arcpy.Project_management(in_dataset=inFC, 
	out_dataset=outFC, 
	out_coor_system="PROJCS['NAD_1983_UTM_Zone_11N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-117.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]", transform_method="", in_coor_system="PROJCS['NAD_1983_StatePlane_California_V_FIPS_0405',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',2000000.0],PARAMETER['False_Northing',500000.0],PARAMETER['Central_Meridian',-118.0],PARAMETER['Standard_Parallel_1',34.03333333333333],PARAMETER['Standard_Parallel_2',35.46666666666667],PARAMETER['Latitude_Of_Origin',33.5],UNIT['Meter',1.0]]", preserve_shape="NO_PRESERVE_SHAPE", max_deviation="", vertical="NO_VERTICAL")


for dirpath, dirnames, filenames in walk:
	for filename in filenames:
		inFile = dirpath + os.sep + filename 
		fDset = inFile.split("\\")[-2]

		outFile = outGDB + os.sep + fDset + os.sep + filename

		reproject(inFile, outFile)


print("Done")

