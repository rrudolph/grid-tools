print("Importing modules")
import arcpy
from icecream import ic
from pathlib import Path


'''
'All_Features_Merge_2022_01_01_fire_only selection cut stump'
'All_Features_Merge_2022_01_01_fire_only selection grasses'
'All_Features_Merge_2022_01_01_fire_only selection OLEU'
'All_Features_Merge_2022_01_01_fire_only by species'
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
'All_Features_Merge_2022_01_01_fire_only foliar backpack'
'Merge_combined'
'All_Features_Merge_2021_01_01_fire_only'
'All_Features_Merge_2022_01_01_fire_only'
'Scorpion_fire_general_polygon'
'Trails'
'Roads'
'NCI_Grid_25m'
'World Imagery'
'''


always_on = ['Scorpion_fire_general_polygon','Trails','Roads','World Imagery']

scenario_dict = {
'2022 Season CIES Invasive Plant Treatments' 					:always_on + ['All_Features_Merge_2022_01_01_fire_only' ],
'2021 and 2022 Season CIES Invasive Plant Treatments' 			:always_on + ['All_Features_Merge_2022_01_01_fire_only', 'All_Features_Merge_2021_01_01_fire_only' ],
'2022 Season CIES Cut Stump Invasive Plant Treatments' 			:always_on + ['All_Features_Merge_2022_01_01_fire_only selection cut stump'],
'2022 Season CIES Foliar Backpack Invasive Plant Treatments' 	:always_on + ['All_Features_Merge_2022_01_01_fire_only foliar backpack'],
'2022 Season CIES Invasive Plant Treatments by Species' 		:always_on + ['2022 fire only by species'],
'2022 Season CIES Invasive Olive Treatments' 					:always_on + ['All_Features_Merge_2022_01_01_fire_only selection OLEU'],
'2022 Season CIES Invasive Grass Species Treatments' 			:always_on + ['All_Features_Merge_2022_01_01_fire_only selection grasses'],

}


outFolder = Path(r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\Reporting")
aprx = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\CHIS Invasives Pro.aprx"
p = arcpy.mp.ArcGISProject(aprx)
lyt = p.listLayouts('Invasives Reporting FY22 CIES')[0]
map_ = p.listMaps('Invasvies Reporting FY22 CIES SCI')[0]
leg = lyt.listElements('LEGEND_ELEMENT')[0]

lyrs = map_.listLayers()

# #######if needed, make a big list of all the layers to pick from
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