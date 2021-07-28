import arcpy

out_grid = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\SBI_Grid.gdb\NCI_Grid_25m_with_SBI_2_sbi_only_12_5m"
in_fc = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\SBI_Grid.gdb\SBI_CUSP2"


print("Generating Grid")S
with arcpy.EnvManager(outputCoordinateSystem="PROJCS['NAD_1983_StatePlane_California_V_FIPS_0405',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',2000000.0],PARAMETER['False_Northing',500000.0],PARAMETER['Central_Meridian',-118.0],PARAMETER['Standard_Parallel_1',34.03333333333333],PARAMETER['Standard_Parallel_2',35.46666666666667],PARAMETER['Latitude_Of_Origin',33.5],UNIT['Meter',1.0]]"):
    arcpy.cartography.GridIndexFeatures(out_grid,
    	in_fc,
    	"INTERSECTFEATURE",
    	"NO_USEPAGEUNIT",
    	None,
    	"12.5 Meters",
    	"12.5 Meters",
    	"1902346.22994347 496424.096019333",
    	None,
    	None,
    	1,
    	"NO_LABELFROMORIGIN")

print("Done")