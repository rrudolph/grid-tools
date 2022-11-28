print("Importing modules")
import arcpy
from icecream import ic
from pathlib import Path


'''
'Cut Stump 2022'
'Grasses 2022'
'OLEU 2022'
'Not Treated or Not Found'
'Fire Perim by Species 2022'
'Features'
'Weed_Point'
'Weed_Line'
'Bread_Crumb_Point'
'Bread_Crumb_Line'
'No_Target_Point'
'No_Target_Line'
'No_Treatment_Point'
'No_Treatment_Line'
'Cut_Line'
'Assignment_Point'
'Assignment_Line'
'Correction_Needed'
'Hidden_Weed_Point'
'Note'
'Fire Perim Foliar 2022'
'Merge_combined'
'Fire Perim 2021'
'Fire Perim 2022'
'Scorpion Fire Perim'
'Trails'
'Roads'
'NCI_Grid_25m'
'World Imagery'
'''


always_on = ['Scorpion_fire_general_polygon','Trails','Roads','World Imagery']

scenario_dict = {
'2022 Season CIES Invasive Plant Treatments' 					:always_on + ['Fire Perim 2022' ],
'2021 and 2022 Season CIES Invasive Plant Treatments' 			:always_on + ['Fire Perim 2022', 'Fire Perim 2021' ],
'2022 Season CIES Cut Stump Invasive Plant Treatments' 			:always_on + ['Cut Stump 2022'],
'2022 Season CIES Foliar Backpack Invasive Plant Treatments' 	:always_on + ['Fire Perim Foliar 2022'],
'2022 Season CIES Invasive Plant Treatments by Species' 		:always_on + ['Fire Perim by Species 2022','Not Treated or Not Found'],
'2022 Season CIES Invasive Olive Treatments' 					:always_on + ['OLEU 2022'],
'2022 Season CIES Invasive Grass Species Treatments' 			:always_on + ['Grasses 2022'],

}


outFolder = Path(r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\Reporting")
aprx = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\CHIS Invasives Pro.aprx"
p = arcpy.mp.ArcGISProject(aprx)
lyt = p.listLayouts('Invasives Reporting FY22 CIES')[0]
map_ = p.listMaps('Invasvies Reporting FY22 CIES SCI')[0]
leg = lyt.listElements('LEGEND_ELEMENT')[0]

lyrs = map_.listLayers()

#######if needed, make a big list of all the layers to pick from
# for lyr in lyrs:
# 	print(f"'{lyr.name}'")


for i, (scenario, vis_vals) in enumerate(scenario_dict.items(), start=1):
	print(scenario, vis_vals)
	for lyr in lyrs:
		if lyr.name in vis_vals:
			lyr.visible = True
		else:
			lyr.visible = False

	title = lyt.listElements("TEXT_ELEMENT", "TITLE")[0]
	title.text = scenario

	
	leg.syncLayerVisibility = True
	print("Exporting jpg")
	lyt.exportToJPEG(outFolder / f"{i} {scenario}.jpg", resolution = 300)

print("Done")