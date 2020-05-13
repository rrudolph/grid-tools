import arcpy, os
try:
    from colorama import Fore, Back, Style, init
    init()
except:
    pass

def Print(text, color="black"):


    if color == "red":
        try:
            print(Back.RED + text+ Style.RESET_ALL)
            arcpy.AddMessage(text)
        except:
            print(text)
            arcpy.AddMessage(text)
    elif color == "yellow":
        try:
            print(Fore.BLACK + Back.YELLOW + text + Style.RESET_ALL)
            arcpy.AddMessage(text)
        except:
            print(text)
            arcpy.AddMessage(text)

    elif color == "green":
        try:
            print(Fore.BLACK + Back.GREEN + text + Style.RESET_ALL)
        except:
            print(text)

    else:
        print(text)
        arcpy.AddMessage(text)



def get_base_name(fc):
	baseName = arcpy.Describe(fc).baseName
	return baseName

def get_unique_values(fc, field):
	# Returns unique values of a field into a sorted list
	with arcpy.da.SearchCursor(fc, [field]) as cursor:
		return sorted({row[0] for row in cursor})

def make_mem_name(fc):
    name = arcpy.Describe(fc).name
    return r"in_memory\{}".format(name)

def add_field(fc, field, fieldLength):
	# Adds a field if it doesn't exists
	fieldNames = [f.name for f in arcpy.ListFields(fc)]
	if field in fieldNames:
		# sys.exit("Field exists! ({})".format(field) +  
		# 	" Might want to check on that before you overwrite it.")
		Print("Field exists.")
		pass
	else:
		arcpy.AddField_management(fc, field, "TEXT", fieldLength)
		Print("Successfully added field: " + field)

def calc_error_field(fc, msg, val):
	# Calculates the sub id based on the input val (or key, 
	# or ID, whatever you want to call it)
	add_field(fc, "OverlapError", 25)
	with arcpy.da.UpdateCursor(fc, ["OID@", "OverlapError"]) as cursor:

		for row in cursor:
			if row[0] == val:
				Print("Found match: " + str(row[0]))

				row[1] = msg
				cursor.updateRow(row)


def get_geom(fc, inputID):
    # Returns a list of geometry from input fc.
    fieldNames = [f.name for f in arcpy.ListFields(fc)]
    if inputID in fieldNames:
        pass
    else:
        inputID = "OID@"

    geom = []
    with arcpy.da.SearchCursor(fc, ["SHAPE@", inputID]) as cursor:
        for row in cursor:
            geom_field = row[0]  
            id_field = row[1]  
            # Print("Getting geometry: Row ID {0}".format(str(id_field)))  
            geom.append((geom_field, id_field))  
    del cursor  
    return geom

def generate_output_grid(out_fc, geom, join_fc, sr):

    Print("Creating output feature class")
    arcpy.CreateFeatureclass_management(os.path.dirname(out_fc),
        os.path.basename(out_fc), 
        "POLYGON", 
        spatial_reference = sr)

    Print("Adding Source ID field")
    arcpy.AddField_management(out_fc, "SOURCE_ID", "TEXT")  

    Print("Adding CutStatus field")
    arcpy.AddField_management(out_fc, "CutStatus", "TEXT")  

    Print("Running insert cursor on new featureclass")
    with arcpy.da.InsertCursor(out_fc, ["SHAPE@", "SOURCE_ID", "CutStatus"]) as icursor:  
        for polygon in geom:  
            # Print(polygon)
            icursor.insertRow(polygon)  
    del icursor

    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(join_fc)
    fieldmappings.addTable(out_fc)

    Print("Spatial Join")
    arcpy.SpatialJoin_analysis(target_features=out_fc, 
        join_features=join_fc, 
        out_feature_class=out_fc + "_joined",
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_COMMON", 
        field_mapping=fieldmappings,
        match_option="INTERSECT", 
        search_radius="", 
        distance_field_name="")

    Print("Adding field name")
    fieldName = get_base_name(join_fc)
    add_field(out_fc + "_joined", "FeatureType", 50)
    arcpy.CalculateField_management(out_fc + "_joined", "FeatureType", "'{}'".format(fieldName), "PYTHON_9.3", "")

def cut(lines, polygons):
	slices = []
	no_cross = []
	crossed_list = []

	for poly, poly_id in polygons:
	        line_count = 0
	        for line, line_id in lines:
	            if line.crosses(poly):
	                Print("{} crosses {}".format(line_id, poly_id))
	                crossed_list.append(poly_id)
	                try:
	                    slice1, slice2 = poly.cut(line)  
	                    slices.insert(0, (slice1, poly_id, "Left Cut"))  
	                    slices.insert(0, (slice2, poly_id, "Right Cut"))
	                except:
	                    slices.insert(0, (poly, poly_id, "Error"))
	            else:
	                Print("{} DOES NOT cross {}".format(line_id, poly_id))
	            line_count += 1

	        if line_count >= len(lines) and poly_id not in crossed_list:
	            no_cross.insert(0, (poly, poly_id, "No Cross"))

	return slices, no_cross