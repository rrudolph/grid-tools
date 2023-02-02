# grid-tools
A series of ArcGIS Python scripts for geoprocessing invasive species data collection using a grid cell polygon base. Invasive species treatments and effort are recorded in esri Field Maps mobile app using a custom set of featureclasses and fields tailored to this type of data collection.  These scripts error check, batch add attribute data, and semi-automate a large amount of geoprocessing tasks to provide a usable output summary of the work and effort of invasive weed treatments. 

![Grid tools screenshot](https://github.com/rrudolph/grid-tools/blob/master/img/grid_tools_screenshot.JPG "Screenshot")

Run using ArcGIS Pro Python 3. Running this script **requires** having a geodatabase set up with the correct featureclasses and fields. 


## Initial Data Download

![ArcGIS Pro Download](https://github.com/rrudolph/grid-tools/blob/master/img/arcpro_download.jpg "Download")
In ArcGIS Pro, zoom to area of interest for processing the grid data with your AGOL feature service the only thing in the map window. In the Map Ribbon, click Download.  this will put it in your current workspace directory as a ".geodatabase" sqlite file. Note the location of this file.  Point the `process invasive treatment grid.py` script to this geodatabase to convert to a ".gdb" file and process the grid data. 


## Process Herbicide Attribute Data
`postprocess herbicide data.py` script will modify the target data download .geodatabase file to populate all herbicide data so the field user does not have to enter it manually.  The script needs the master excel spreadsheet that has the formulation codes that match up with the formulation codes the user entered during herbicide application.  Using  the formulation code as a lookup key, the script enters the herbicide trade name, concentration, and other pertinent data into the specified mobile geodatabase.  Once processed and inspected, the offline copy can be synced back with AGOL.

## Error Checking
`error check agol fcs.py` only inspects common attribute errors that may need to be manually fixed by field user input. This script reads the .geodatabase offline sync file and prints out an error table to screen.  It does not modify any input data. Once any data discrepancies are fixed in the offline .geodatabase, the data can by synced back to AGOL.

## Automate Geoprocessing of Grid Cell Data
`process invasive treatment grid.py` script is a series of many geoprocessing tasks that are designed to generate "on demand" area polygons of invasive treatment data based on the established "grid" overlay for the islands. For example, a GIS specialist can download an offline copy of a certain area or the entire region of invasive treatment data to a mobile geodatabase as described above.  The user can then point this script to that .geodatabase file to process the grid data for that specified area.  There is a substantial amount of processing that can take quite a bit of time depending on the area and time frame chosen.  

Edit variables at the bottom of the script before running. 
`data_ws` is the workspace path to the .geodatabase file. 
`in_grid` is the grid file that the script needs in order to process the spatial join for each species treated. 
`scratch_ws` is the scratch workspace that generates temporary data and the final output merged grid product.  Most of the data in here is for debugging purposes or to inspect output as the script iterates over each species.  The final 'All_Features_Merge' product is typically where the herbicide and acres totals are calculated by the GIS specialist. 


The `config.yaml` yaml file typically does not need editing.  It's where I stored some field names, projection strings, and other data that I didn't want to clutter up the script with. 
