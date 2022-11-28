import pytz
import datetime
import arcpy

# from pytz import common_timezones
# print(common_timezones)

now_utc = datetime.datetime.utcnow()

tz = pytz.timezone('US/Pacific')
# now_local = now_utc.replace(tzinfo=pytz.utc).astimezone(tz)
# print(now_utc)
# print(type(now_utc))
# print(now_local)
# print(type(now_local))


## To do all the fcs
ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\Feature Downloads\Features_09AB5B7F24494A77884651D4489996B9.geodatabase"
arcpy.env.workspace = ws
fcs = arcpy.ListFeatureClasses()

print(fcs)

for fc in fcs:

    print(f"------- Fixing time for {fc} with {arcpy.GetCount_management(fc)[0]} features ------------")
    fields = [field.name for field in arcpy.ListFields(fc)]
    if "Action_Date_Local" in fields:
        with arcpy.da.UpdateCursor(fc, ['Action_Date', 'Action_Date_Local']) as cursor:
            for row in cursor:
                if not row[1] and row[0]:
                    local_update = row[0].replace(tzinfo=pytz.utc).astimezone(tz)
                    print(f"{row[0]}  ->  {row[1]} -> {local_update}")
                    row[1] = local_update
                    cursor.updateRow(row)