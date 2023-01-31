

print("Importing modules")
import arcpy, os
arcpy.env.overwriteOutput = True

rootDir = r"C:\GIS\Projects\CHIS Invasives\Domain Update Jan2023"

inWorkspace = os.path.join(rootDir, "Features_FD64BA1E1B2E479B8F1E98DB0C7B3828_MobileGdbToFileGdb.gdb")

# domain_list = ["DOM_DataRecorder", "DOM_InvasiveSpecies"]
domain_list = [domain for domain in arcpy.da.ListDomains(inWorkspace)]

for domain in domain_list:
    domainName = domain.name
    print(f"********* {domainName} *********")
    if domain.domainType == 'CodedValue':
        coded_values = domain.codedValues
        for val, desc in coded_values.items():
            print('{0}'.format(val))

    print()
    print()

    # outTable = os.path.join(rootDir, domainName + "_DomainToTable.csv")

    # print("Running table to domain...")
    # arcpy.DomainToTable_management(in_workspace=inWorkspace,
    #   domain_name=domainName,
    #   out_table=outTable,
    #   code_field="Code",
    #   description_field="Description",
    #   configuration_keyword="")

    # arcpy.TableToTable_conversion(outTable, os.path.join(rootDir, "Domain files"), domainName + ".csv")

# print("Done.")