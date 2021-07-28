
input_id = "IDPK"

print_("Calculating number of crosses on grid cells")
counter = Counter(master_cross_list)
print(f"Master cross list count: {counter}")
add_field(final_fc, "Times_Crossed", 25)
with arcpy.da.UpdateCursor(final_fc, [input_id, "Times_Crossed"]) as cursor:

    for row in cursor:
        for id_, count in master_cross_list.items():
            if row[0] == id_:
                print_(f"Found match: {row[0]}")

                row[1] = count
                cursor.updateRow(row)
