

print("Importing modules")
import arcpy, os
arcpy.env.overwriteOutput = True

rootDir = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427"
scratch_ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\scratch.gdb"

inWorkspace = os.path.join(rootDir, "NChannelIslandsTreatmentTemplate.gdb")

# domain_list = ["DOM_DataRecorder", "DOM_InvasiveSpecies"]
domain_list = [domain.name for domain in arcpy.da.ListDomains(inWorkspace)]

for domainName in domain_list:
	print(domainName)
	outTable = os.path.join(scratch_ws, domainName + "_DomainToTable")

	print("Running table to domain...")
	arcpy.DomainToTable_management(in_workspace=inWorkspace,
		domain_name=domainName,
		out_table=outTable,
		code_field="Code",
		description_field="Description",
		configuration_keyword="")

	arcpy.TableToTable_conversion(outTable, os.path.join(rootDir, "Domain files"), domainName + ".csv")

print("Done.")