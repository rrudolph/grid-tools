import arcpy, os

def get_projection_name(fc):
	spatial_ref = arcpy.Describe(fc).spatialReference
	return spatial_ref.name


def get_fc_list(inWS:"Input workspace") -> "Full list of featureclasses":
	"""Temporarily sets the workspace and returns the full path and name of each fc."""
	return_ = []
	with arcpy.EnvManager(workspace=inWS):
		fcs = arcpy.ListFeatureClasses()
		for fc in fcs:
			desc = arcpy.Describe(fc)
			catPath = desc.catalogPath
			return_.append(catPath)
	return return_

def make_projected_gdb(gdb):
	gdb_name = arcpy.Describe(gdb).name
	projected_name = gdb_name.split(".")[0] + "_projected." + gdb_name.split(".")[1]
	dir_name = os.path.dirname(gdb)
	return_name = os.path.join(dir_name, projected_name)
	print(f"Making new fileGDB: {return_name}")
	arcpy.management.CreateFileGDB(dir_name, projected_name, "CURRENT")
	return return_name


def project_all_fcs(gdb):
	# proj_gdb = make_projected_gdb(gdb)

	fcs = get_fc_list(gdb)
	for fc in fcs:
		name = arcpy.Describe(fc).name
		print(f"Projecting {fc}, was {get_projection_name(fc)}")
		# arcpy.management.Project(fc, os.path.join(proj_gdb, name), "PROJCS['NAD_1983_StatePlane_California_V_FIPS_0405',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',2000000.0],PARAMETER['False_Northing',500000.0],PARAMETER['Central_Meridian',-118.0],PARAMETER['Standard_Parallel_1',34.03333333333333],PARAMETER['Standard_Parallel_2',35.46666666666667],PARAMETER['Latitude_Of_Origin',33.5],UNIT['Meter',1.0]]", "WGS_1984_(ITRF00)_To_NAD_1983", "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]", "NO_PRESERVE_SHAPE", None, "NO_VERTICAL")


data_ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\Features_C297D1B8EFC54A7B9932F794F6825C83.gdb"

project_all_fcs(data_ws)