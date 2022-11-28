import arcpy

fc = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch_buffer_isthmus_test.gdb\Weed_Line_Foeniculum_vulgare_temp_spp_select_to_buffer_18_union"

def get_buffered_area(fc):
    '''
    Inputs a featureclass that is a buffered weed line.
    Returns the total area buffered in acres. 
    Used for the part of the script that buffered weed lines along roads and trails.  Data needs to be proportional across the
    grid cells that is intersected by the buffered area for a given ween line treatment. This total buffered area is part of the
    calculation to do that proportional herbicide treatment value. 
    '''
    arcpy.management.CalculateGeometryAttributes(fc, "gross_Acres AREA", '', "ACRES", 'PROJCS["NAD_1983_StatePlane_California_V_FIPS_0405",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",2000000.0],PARAMETER["False_Northing",500000.0],PARAMETER["Central_Meridian",-118.0],PARAMETER["Standard_Parallel_1",34.03333333333333],PARAMETER["Standard_Parallel_2",35.46666666666667],PARAMETER["Latitude_Of_Origin",33.5],UNIT["Meter",1.0]]', "SAME_AS_INPUT")
    total_area = []
    fields = ['gross_Acres', 'Action_Type']
    with arcpy.da.SearchCursor(fc, fields) as cursor:
        for row in cursor:
            print(f'{row[0]}, {row[1]}')
            if row[1] in ['Weed_Line']:
                print("Appending to total area list")
                total_area.append(row[0])
    return sum(total_area)


buffered_area = get_buffered_area(fc)

print("Adding field")
arcpy.management.AddField(fc, "original_finished_ounces", "DOUBLE", None, None, None, "Original Finished Ounces Applied", "NULLABLE", "NON_REQUIRED", '')


#               0                     1                       2              3
fields = ['finished_Ounces', 'original_finished_ounces', 'Action_Type', 'gross_Acres']
with arcpy.da.UpdateCursor(fc, fields) as cursor:
    for row in cursor:
        if row[2] in ['Weed_Line']:
            row[1] = row[0] # Keep a record of the original ounces value
            row[0] = (row[3] / buffered_area) * row[0] # get ounces proportional to the area and total applied for the line
            cursor.updateRow(row)
