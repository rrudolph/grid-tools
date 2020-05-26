import arcpy, os

ws = r"C:\GIS\Projects\CHIS Invasive GeoDB testing\WildLands_Grid_System_20200427\NChannelIslandsTreatmentTemplate.gdb"
arcpy.env.workspace = os.path.join(ws, "TreatmentFiles")
arcpy.env.overwriteOutput =True

def field_order_lookup(fc):
    '''
    Returns the reordered field list by fc name
    '''
    switcher = {
    "Assignment_Line": ['OBJECTID', 'Shape', 'Action_Date', 'Action_Date_Local','Assigned', 'Assigned_By', 'Note', 'Shape__Length', 'Filter_1', 'Filter_2', 'Filter_3', 'Shape_Length' ],
    "Assignment_Point": ['OBJECTID', 'Shape', 'Action_Date', 'Action_Date_Local', 'Assigned', 'Assigned_By', 'Note', 'Filter_1', 'Filter_2', 'Filter_3'],
    "Bread_Crumb_Line": ['OBJECTID', 'Shape', 'Action_Date', 'Action_Date_Local', 'Note', 'Shape__Length', 'Filter_1', 'Filter_2', 'Filter_3', 'Shape_Length'],
    "Bread_Crumb_Point": ['OBJECTID', 'Shape', 'Action_Date', 'Action_Date_Local', 'Note', 'Filter_1', 'Filter_2', 'Filter_3'],
    "Correction_Needed": ['OBJECTID', 'Shape', 'Action_Date', 'Action_Date_Local', 'Observer', 'Issue', 'Issue_Other', 'Note', 'CreationDate', 'Creator', 'EditDate', 'Editor'],
    "Cut_Line": ['OBJECTID', 'Shape', 'Action_Date', 'Action_Date_Local', 'Staff', 'Species', 'Note', 'Shape_Length'],
    "Hidden_Weed_Point": ['OBJECTID', 'Shape', 'Action_Date', 'Action_Date_Local', 'Species', 'Note', 'Filter_1', 'Filter_2', 'Filter_3'],
    "No_Target_Line": ['OBJECTID', 'Shape', 'Action_Date', 'Action_Date_Local', 'Entered_By', 'Species1', 'Species2', 'Species3', 'Species4', 'Species5', 'Note', 'Shape__Length', 'grid_Scale', 'Filter_1', 'Filter_2', 'Filter_3', 'Shape_Length'],
    "No_Target_Point": ['OBJECTID', 'Shape', 'Action_Date', 'Action_Date_Local', 'Entered_By', 'Species1', 'Species2', 'Species3', 'Species4', 'Species5', 'Note', 'grid_Scale', 'Filter_1', 'Filter_2', 'Filter_3'],
    "No_Treatment_Line": ['OBJECTID', 'Shape', 'Action_Date', 'Action_Date_Local', 'Entered_By', 'Species1', 'Species2', 'Species3', 'Species4', 'Species5', 'Limitations', 'Lim_Other', 'Note', 'Shape__Length', 'grid_Scale', 'Filter_1', 'Filter_2', 'Filter_3', 'Shape_Length'],
    "No_Treatment_Point": ['OBJECTID', 'Shape', 'Action_Date', 'Entered_By', 'Species1', 'Species2', 'Species3', 'Species4', 'Species5', 'Limitations', 'Lim_Other', 'Note', 'grid_Scale', 'Filter_1', 'Filter_2', 'Filter_3'],
    "Note": ['OBJECTID', 'Shape', 'Action_Date', 'Action_Date_Local', 'Entered_By', 'Note', 'Photo_Taken', 'Filter_1', 'Filter_2', 'Filter_3'],
    "Weed_Line": ['OBJECTID', 'Shape', 'Action_Date', 'Action_Date_Local', 'project', 'contract_Number', 'applicator', 'weed_Target', 'weed_Target_Other', 'road_Sides', 'meter_Buffer_Distance', 'number_Individuals', 'percent_Target', 'treatment_Mode', 'DyneAmic', 'Grounded', 'formulation_Code', 'formulation_Other', 'finished_Gallons', 'finished_Ounces', 'retreat', 'percent_Dead_Integer', 'percent_Dead_Decimal', 'treatment_Note', 'asso_Species_1', 'asso_Species_2', 'asso_Species_3', 'asso_Species_4', 'asso_Species_5', 'asso_Species_total', 'scientific_Name', 'common_Name', 'chemical_1', 'chemical_1_Trade', 'chem_1_EPA', 'chem_1_WetRate', 'chem_1_DryRate', 'chem_1_Gallons', 'chem_1_Density', 'chem_1_Ounces', 'chem_1_Pounds', 'chem_2', 'chemical_2_Trade', 'chem_2_EPA', 'chem_2_WetRate', 'chem_2_DryRate', 'chem_2_Gallons', 'chem_2_Density', 'chem_2_Ounces', 'chem_2_Pounds', 'adjuvant_1_Trade', 'adjuvant_1_EPA', 'adjuvant_1_Rate', 'adjuvant_2_Trade', 'adjuvant_2_EPA', 'adjuvant_2_Rate', 'net_Acres', 'gross_Acres', 'note', 'Filter_1', 'Filter_2', 'Filter_3', 'Shape_Length'],
    "Weed_Point": ['OBJECTID', 'Shape', 'Action_Date', 'Action_Date_Local', 'project', 'contract_Number', 'applicator', 'weed_Target', 'weed_Target_Other', 'number_Individuals', 'percent_Target', 'treatment_Mode', 'DyneAmic', 'Grounded', 'formulation_Code', 'formulation_Other', 'finished_Gallons', 'finished_Ounces', 'retreat', 'percent_Dead_Integer', 'percent_Dead_Decimal', 'treatment_Note', 'asso_Species_1', 'asso_Species_2', 'asso_Species_3', 'asso_Species_4', 'asso_Species_5', 'asso_Species_total', 'scientific_Name', 'common_Name', 'chemical_1', 'chemical_1_Trade', 'chem_1_EPA', 'chem_1_WetRate', 'chem_1_DryRate', 'chem_1_Gallons', 'chem_1_Density', 'chem_1_Ounces', 'chem_1_Pounds', 'chem_2', 'chemical_2_Trade', 'chem_2_EPA', 'chem_2_WetRate', 'chem_2_DryRate', 'chem_2_Gallons', 'chem_2_Density', 'chem_2_Ounces', 'chem_2_Pounds', 'adjuvant_1_Trade', 'adjuvant_1_EPA', 'adjuvant_1_Rate', 'adjuvant_2_Trade', 'adjuvant_2_EPA', 'adjuvant_2_Rate', 'net_Acres', 'gross_Acres', 'note', 'Filter_1', 'Filter_2', 'Filter_3']
    }
    return switcher.get(fc, "Error") 


def make_lookup_dict(fclist):
    for fc in fclist:
        fieldNames = [f.name for f in arcpy.ListFields(fc)]
        print(f'"{fc}": {fieldNames},')

def delete_reorder_fields(inWS:"Input workspace"):
    '''
    Temporarily sets the workspace and deletes layers that meet a criteria. 
    '''

    with arcpy.EnvManager(workspace=inWS):
        fcs = arcpy.ListFeatureClasses("*_reorder")
        for fc in fcs:
            print("Deleting " + fc)
            arcpy.Delete_management(fc)



def reorder_fields(table, out_table, field_order, add_missing=True):
    """ 
    this function courtesy of https://gis.stackexchange.com/questions/32119/reordering-fields-permanently-in-file-geodatabase-using-arcgis-desktop
    Reorders fields in input featureclass/table
    :table:         input table (fc, table, layer, etc)
    :out_table:     output table (fc, table, layer, etc)
    :field_order:   order of fields (objectid, shape not necessary)
    :add_missing:   add missing fields to end if True (leave out if False)
    -> path to output table
    """
    existing_fields = arcpy.ListFields(table)
    existing_field_names = [field.name for field in existing_fields]

    existing_mapping = arcpy.FieldMappings()
    existing_mapping.addTable(table)

    new_mapping = arcpy.FieldMappings()

    def add_mapping(field_name):
        mapping_index = existing_mapping.findFieldMapIndex(field_name)

        # required fields (OBJECTID, etc) will not be in existing mappings
        # they are added automatically
        if mapping_index != -1:
            field_map = existing_mapping.fieldMappings[mapping_index]
            new_mapping.addFieldMap(field_map)

    # add user fields from field_order
    for field_name in field_order:
        if field_name not in existing_field_names:
            raise Exception("Field: {0} not in {1}".format(field_name, table))

        add_mapping(field_name)

    # add missing fields at end
    if add_missing:
        missing_fields = [f for f in existing_field_names if f not in field_order]
        for field_name in missing_fields:
            add_mapping(field_name)

    # use merge with single input just to use new field_mappings
    arcpy.Merge_management(table, out_table, new_mapping)
    return out_table


fcs = arcpy.ListFeatureClasses()

# delete_reorder_fields(arcpy.env.workspace)

# make_lookup_dict(fcs)

for fc in fcs:
    out_fc = fc + "_reorder"
    print("-----" + fc)
    reorder_fields(fc, out_fc, field_order_lookup(fc))
