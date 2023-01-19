# grid-tools
ArcGIS Python toolbox for geoprocessing invasive species data collection using a grid cell polygon base. 

![Grid tools screenshot](https://github.com/rrudolph/grid-tools/blob/master/img/grid_tools_screenshot.JPG "Screenshot")

Run using ArcGIS Pro Python 3. Running this script **requires** having a geodatabase set up with the correct featureclasses and fields. 


## Initial Data Download

![ArcGIS Pro Download](https://github.com/rrudolph/grid-tools/blob/master/img/arcpro_download.jpg "Download")
In ArcGIS Pro, zoom to area of interest for processing the grid data with your AGOL feature service the only thing in the map window. In the Map Ribbon, click Download.  this will put it in your current workspace directory as a ".geodatabase" sqlite file.  Point the `process invasive treatment grid.py` script to this geodatabase to convert to a ".gdb" file and process the gid data. 


## Process Herbicide Data
`postprocess herbicide data.py` script will modify the target data download .geodatabase file to populate all herbicide data so the field user does not have to enter it manually.  The script needs the master excel spreadsheet that has the formulation codes that match up with the formulation codes the user entered during herbicide application.  Using that formulation code, the script enters the herbicide trade name, concentration, and other pertinent data

## Error Checking
`error check agol fcs.py`

## Process the Data
`process invasive treatment grid.py`



