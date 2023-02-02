'''
Make a compressed zip file of the CHIS Invasives Grid AGOL database.
Script makes a new file GDB, adds all feature services to it, compresses
it, then deletes the GDB. Also logs all activity. 

Useful in case AGOL gets hacked, corrupted, or users accidentally delete/screw up. 

Optionally use windows Task Scheduler to automatically run at desired interval.

Used to use a tar file to compress but it was giving me issues with the .lock file.
For those older tar files: to extract, use cygwin or powershell
command line example: tar -xzvf AGOL_Grid_DB_Backup_20210630091023.gdb.tar.gz
will unpack to make AGOL_Grid_DB_Backup_20210630091023.gdb in the same folder.

R. Rudolph, GISP, Channel Islands National Park
rocky_rudolph@nps.gov, 6/30/2021
'''


import arcpy
import time
import logging
import os
from os.path import join
from arcgis.gis import GIS
import re

# Optional debugger 
try:
	from icecream import ic
except:
	pass

# Functions
def plog(msg, msg_type="info"):
	'''Print and log at the same time'''
	print(msg)
	if msg_type == "info":
		logger.info(msg)
	if msg_type == "error":
		logger.error(msg)

def strip_non_alphanum(string):
    return re.sub('[^0-9a-zA-Z]+', '_', string)


# Vars
backup_folder = r"C:\GIS\Projects\CHIS Invasives\Archive"
now = time.strftime('%Y%m%d%H%M%S')
db_name = f"AGOL_Grid_DB_Backup_{now}"
out_db = os.path.join(backup_folder, f"{db_name}.gdb")

## Set up logger
LOG_FORMAT = "%(levelname)s %(asctime)s - line %(lineno)d - %(message)s"
logging.basicConfig(filename = join(backup_folder, "Grid_DB_backup.log"),
	level = logging.INFO,
	format = LOG_FORMAT,
	datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()

plog(f"Connecting to AGOL")
gis = GIS("pro")
## Vars for tool
item_id = '3f3e5cdced0340b494bcdce647809ca0'
export_type = "File Geodatabase"

data_item = gis.content.get(item_id)
data_title = strip_non_alphanum(data_item['title'])
plog(f"[+] Processing {data_title}")
temp_file = time.strftime(f"{data_title}_backup_%Y%m%d_%H%M")
plog(f"....Generatring temporary {export_type}: {temp_file}")
data_item.export(temp_file, export_type, parameters=None, wait=True)
exported_temp = gis.content.search(temp_file, item_type=export_type)
# ic(exported_file)
exported_file = gis.content.get(exported_temp[0].itemid)
username = exported_file['owner']
export_name = exported_file['name']
new_export_name = export_name.replace('.zip', f'_{username}.zip')
# ic(exported_file)
plog(f"....Downloading as {export_type}")
exported_file.download(save_path=backup_folder)
os.rename(join(backup_folder, export_name), join(backup_folder, new_export_name))
plog(f"....Removing {export_type} backup online") # No need to keep. Saves AGOL user account space. 
exported_file.delete()
plog("....Download complete")

plog("Backup complete.")
