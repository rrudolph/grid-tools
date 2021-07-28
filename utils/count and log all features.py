'''
Counts all invasive grid featureclasses in AGOL and writes to a log.
Updated 6/15/2021
R. Rudolph
'''

import arcpy
import sys
import logging
from icecream import ic

# Create and configure logger
LOG_FORMAT = "%(levelname)s %(asctime)15s - %(message)s"

# If file doesn't exist, it will be created.  Append is default.
logging.basicConfig(filename = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\fc_count_log.log",
	level = logging.DEBUG,
	format = LOG_FORMAT,
	datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger() 

def get_fc_count(fc):
	return arcpy.management.GetCount(fc)[0]

def print_log(msg):
	print(msg)
	logger.info(msg)

base_url = "https://services1.arcgis.com/fBc8EJBxQRMcHlei/arcgis/rest/services/Features/FeatureServer/"

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

for name, url in fc_dict.items():
	count = get_fc_count(url)
	print_log(f"{name}: {count}")