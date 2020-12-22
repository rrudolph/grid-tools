# grid-tools
ArcGIS Python toolbox for geoprocessing invasive species data collection using a grid cell polygon base. 

![Grid tools screenshot](https://github.com/rrudolph/grid-tools/blob/master/img/grid_tools_screenshot.JPG "Screenshot")

Can be run within ArcGIS Pro ~or ArcMap~ as a python toolbox or stand alone script. Sorry, I'm starting to move away from ArcMap/Python2.

If you run as a toolbox, make sure to change line 8 to False like so:

```python
run_stand_alone = False
```

Running this script **requires** having a geodatabase set up with the correct featureclasses and fields. 


Updated workflow

![ArcGIS Pro Download](https://github.com/rrudolph/grid-tools/blob/master/img/arcpro_download.png "Download")
In ArcGIS Pro, zoom to area of interest for processing the grid data. In the Map Ribbon, click Download.  this will put it in your current workspace directory as a ".geodatabase" sqlite file.  Point the script to this geodatabase to convert to a ".gdb" file and process the gid data. 