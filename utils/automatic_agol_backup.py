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
import zipfile

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


def zip_ws(path, zip):
	'''Zip a file gdb, skip lock files'''
	global zip_success
	try:
		files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
		for file in files:
			if not file.endswith('.lock'):
				print(f"Zipping {file}...")
				try:
					zip.write(os.path.join(path, file), arcname=file)

				except Exception as e:
					print(f"    Error adding {file}: {e}")

		plog("Zip successful")
		zip_success = True

	except Exception as e:
		plog(f"Zip failed: {e}")
		zip_success = False

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

		
	except Exception as e:
		plog(f"An error occurred with {fc_name}. Message: {e}", "error")


	try:
		out_zip = out_db + ".zip"
		plog(f"Generating zip file: {out_zip}")
		with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as zip_file:
			zip_ws(out_db, zip_file)

		if zip_success:
			plog(f"Deleting file gdb... {out_db}")
			arcpy.Delete_management(out_db)

	except Exception as e:
		plog(f"Error making zip file. Message: {e}", "error")


if __name__ == '__main__':
	main()