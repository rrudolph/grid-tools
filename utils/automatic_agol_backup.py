'''
Make a compressed tar file of the CHIS Invasives Grid AGOL database.
Script makes a new file GDB, adds all feature services to it, compresses
it, then deletes the GDB. Also logs all activity. 

Useful in case AGOL gets hacked, corrupted, or users accidentally delete/screw up. 

Optionally use windows Task Scheduler to automatically run at desired interval.

To extract, use cygwin or powershell
command line example: tar -xzvf AGOL_Grid_DB_Backup_20210630091023.gdb.tar.gz
will unpack to make AGOL_Grid_DB_Backup_20210630091023.gdb in the same folder.

R. Rudolph, GISP, Channel Islands National Park
rocky_rudolph@nps.gov, 6/30/2021
'''


import arcpy
import time
import logging
import os
import tarfile

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


def make_tarfile(source):
	''' Generate a compressed tarfile'''
	# archive name is name of gdb, to prevent it from extracting into a big tree of folders
	arcname = source.split("\\")[-1]
	# ic(arcname)
	target = f"{source}.tar.gz"
	plog(f"Making tarfile {target}")
	with tarfile.open(target, "w:gz") as tar:
		tar.add(source, arcname=arcname)

def get_fc_count(fc):
	''' Get the number of features. Optional but good to log '''
	return arcpy.management.GetCount(fc)[0]

# Vars
archive_dir = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\Archive"
base_url = "https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Features/FeatureServer/"
now = time.strftime('%Y%m%d%H%M%S')
db_name = f"AGOL_Grid_DB_Backup_{now}"
out_db = os.path.join(archive_dir, f"{db_name}.gdb")


# Dictionary of AGOL fcs URLs
fc_dict ={
	"weed_point" 			: f"{base_url}0",
	"weed_line" 			: f"{base_url}1",
	"bread_crumb_point" 	: f"{base_url}2",
	"bread_crumb_line" 		: f"{base_url}3",
	"no_target_point" 		: f"{base_url}4",
	"no_target_line" 		: f"{base_url}5",
	"no_treatment_point" 	: f"{base_url}6",
	"no_treatment_line" 	: f"{base_url}7",
	"cut_line" 				: f"{base_url}8",
	"assignment_point" 		: f"{base_url}9",
	"assignment_line" 		: f"{base_url}10",
	"correction_needed" 	: f"{base_url}11",
	"hidden_weed_point" 	: f"{base_url}12",
	"note" 					: f"{base_url}13"
}


# Create and configure logger
LOG_FORMAT = "%(levelname)s %(asctime)s - line %(lineno)d - %(message)s"

# If file doesn't exist, it will be created.  Append is default.
logging.basicConfig(filename = os.path.join(archive_dir, "Grid_DB_backup.log"),
	level = logging.INFO,
	format = LOG_FORMAT,
	datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()

def main():
	''' Main script '''
	try:
		plog(f"Creating {db_name}")
		arcpy.management.CreateFileGDB(archive_dir, db_name, "CURRENT")

		for fc_name, url in fc_dict.items():
			feat_count = get_fc_count(url)
			arcpy.conversion.FeatureClassToFeatureClass(url, 
				out_db, 
				fc_name,
				None, None, None)
			plog(f"Success downloading {fc_name}. Feature count: {feat_count}")

		make_tarfile(out_db)
		
		arcpy.management.Delete(out_db)
		plog(f"Deleted {out_db}")


	except Exception as e:
		plog(f"An error occurred with {fc_name}. Message: {e}", "error")

if __name__ == '__main__':
	main()