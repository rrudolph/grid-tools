
import tarfile
from icecream import ic

def make_tarfile(source):
	''' Generate a compressed tarfile'''
	# archive name is name of gdb, to prevent it from extracting into a big tree of folders
	arcname = source.split("\\")[-1]
	# ic(arcname)
	target = f"{source}.tar.gz"
	ic(f"Making tarfile {target}")
	with tarfile.open(target, "w:gz") as tar:
		tar.add(source, arcname=arcname)

db = r"C:\\GIS\\Projects\\CHIS Invasive GeoDB testing\\WildLands_Grid_System_20200427\\Archive\\AGOL_Grid_DB_Backup_20211025170455.gdb"

make_tarfile(db)