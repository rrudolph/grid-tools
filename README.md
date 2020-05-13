# grid-tools
ArcGIS Python toolbox for geoprocessing invasive species data collection using a grid cell polygon base. 

![Grid tools screenshot](https://github.com/rrudolph/grid-tools/blob/master/img/grid_tools_screenshot.JPG "Screenshot")

Can be run within ArcGIS Pro or ArcMap as a python toolbox or stand alone script.

If you run as a toolbox, make sure to change line 8 to False like so:

```python
run_stand_alone = False
```

Running this script **requires** having a geodatabase set up with the correct featureclasses and fields.

