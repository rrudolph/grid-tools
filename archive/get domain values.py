import arcpy

def printWrite(data):
	print(data)
	f.write(str(data) + "\n")

domains = arcpy.da.ListDomains(r"C:\Temp\SantaCruzIsland_WeedTreatment_20200427\NChannelIslandsTreatmentTemplate.gdb")
fname = r"C:\Temp\SantaCruzIsland_WeedTreatment_20200427\domains.txt"

with open(fname, "w", encoding="utf-8") as f:

	for domain in domains:
		printWrite('Domain name: {0}'.format(domain.name))
		if domain.domainType == 'CodedValue':
			coded_values = domain.codedValues
			for val, desc in coded_values.items():
				printWrite('{0} : {1}'.format(val, desc.encode("utf-8")))
		elif domain.domainType == 'Range':
			printWrite('Min: {0}'.format(domain.range[0]))
			printWrite('Max: {0}'.format(domain.range[1]))