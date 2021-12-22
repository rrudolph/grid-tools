from os import listdir
from os.path import isfile, join
import zipfile


def zip_ws(path, zip):

    files = [f for f in listdir(path) if isfile(join(path, f))]
    
    for file in files:
        if not file.endswith('.lock'):
            print(f"Zipping {file}...")
            try:
                zip.write(join(path, file), arcname=file)

            except Exception as e:
                print(f"    Error adding {file}: {e}")



db = r"C:\\GIS\\Projects\\CHIS Invasive GeoDB testing\\WildLands_Grid_System_20200427\\Archive\\AGOL_Grid_DB_Backup_20211025180305.gdb"
outfile = r"C:\\GIS\\Projects\\CHIS Invasive GeoDB testing\\WildLands_Grid_System_20200427\\Archive\\AGOL_Grid_DB_Backup_20211025180305.gdb.zip"

with zipfile.ZipFile(outfile, 'w', zipfile.ZIP_DEFLATED) as zip_file:

    zip_ws(db, zip_file)
