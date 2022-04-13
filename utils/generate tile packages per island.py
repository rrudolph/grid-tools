
import arcpy
import re
from os.path import join
from time import time
import humanfriendly
  
  
def timer_func(func):
    # This function shows the execution time of 
    # the function object passed
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f'Function {func.__name__!r} executed in {humanfriendly.format_timespan((t2-t1))}')
        return result
    return wrap_func


def strip_non_alphanum(string):
    return re.sub('[^0-9a-zA-Z]+', '_', string)

@timer_func
def make_package(map_, name, extent):
    arcpy.CreateMapTilePackage_management(map_,
        "ONLINE",
        join(base_dir, "Grid tile package", f"CHIS_Grid_Tile_Package_{strip_non_alphanum(name)}_25m_14.tpk"),
        "MIXED",
        "14",
        package_type = "TPK",
        summary = f"CHIS grid tile package for {name}",
        extent = extent)



arcpy.env.overwriteOutput = True

base_dir = "C:\\GIS\\Projects\\CHIS Invasive GeoDB testing\\WildLands_Grid_System_20200427"

# p = arcpy.mp.ArcGISProject("CURRENT")
proj_path = join(base_dir,"CHIS Invasives Pro.aprx")
p = arcpy.mp.ArcGISProject(proj_path)
map_ = p.listMaps("Tile Package*")[0]
print(f"Map name: {map_.name} -- Spatial reference: {map_.spatialReference.name}")
lyrs = map_.listLayers("CHIS_tile*")

extent_dict = {}
for lyr in lyrs:
    print(f"Extracting extents for Layer {lyr.name}")
    with arcpy.da.SearchCursor(lyr, ['SHAPE@', 'Name']) as cursor:
        for row in cursor:
            extent = row[0].extent
            name = row[1]
            extent_dict.update([(name, extent)])

# print(extent_dict)

for name, extent in extent_dict.items():
    if name == "Santa Barbara":

        print(f"Generating tile package for {name} using \
            XMin: {extent.XMin} \
            YMin: {extent.YMin} \
            XMax: {extent.XMax} \
            YMax: {extent.YMax}")

        make_package(map_, name, extent)


print("Done")