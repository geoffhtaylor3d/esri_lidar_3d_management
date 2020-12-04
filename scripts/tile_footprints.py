from arcpy import ddd
from arcpy.management import Delete, Sort, AddField, DeleteField
from os.path import join
from arcpy import da
from arcpy.analysis import Intersect
from collections import Counter

# User Input Parameters
in_buildings = r'C:\Users\geof7015\Documents\ArcGIS\Projects\Ohio_LiDAR_Demo\Ohio_LiDAR_Demo.gdb\Building_3D_manual'
building_fid = "bldg_fid"
in_tiles = r'C:\Users\geof7015\Documents\ArcGIS\Projects\Leveraging_LiDAR\tiles\tiles.shp\tiles'
tile_fid = 'FID_tiles'
file_name = 'FileName'

# Constants - DO NOT MODIFY
split_area = "split_area"
orig_area = "orig_area"

# Begin Script


def calc_area(in_fc, field_name):
    AddField(in_fc, field_name, "DOUBLE")
    with da.UpdateCursor(in_fc, [field_name, "SHAPE@AREA"]) as cursor:
        for r in cursor:
            r[0] = r[1]
            cursor.updateRow(r)


def field_exists(in_fc, in_field):
    from arcpy import ListFields
    if in_field in [f.name for f in ListFields(in_fc)]:
        return True
    else:
        return False


def delete_field_if_exists(in_fc, in_field):
    if field_exists(in_fc, in_field):
        DeleteField(in_fc, in_field)


assert field_exists(in_buildings, building_fid), \
    "no attribute named {} in feature class".format(building_fid)


for field in [tile_fid, file_name]:
    delete_field_if_exists(in_buildings, field)

temp_fp = join("in_memory", "mp_fp")
ddd.MultiPatchFootprint(in_buildings, temp_fp, "bldg_fid")

calc_area(in_fc=temp_fp, field_name=orig_area)

temp_isect = join("in_memory", "temp_isect")
Intersect(r"{0} #;{1} #".format(temp_fp, in_tiles), temp_isect, "ALL", None, "INPUT")

# Delete Temporary Multipatch Footprint
Delete(temp_fp)

calc_area(in_fc=temp_isect, field_name=split_area)

temp_isect_asc = join("in_memory", "temp_isect_asc")
Sort(temp_isect, temp_isect_asc, [[building_fid, "ASCENDING"]])
# Delete Temporary Intersect Feature Class
Delete(temp_isect)

fields = [building_fid, tile_fid, file_name, orig_area, split_area]

# Generate a list of duplicates

bldg_list = []
with da.SearchCursor(temp_isect_asc, building_fid) as cursor:
    for row in cursor:
        bldg_list.append(row[0])

duplicates = [item for item, count in Counter(bldg_list).items() if count > 1]

duplicates_list = []
for i in duplicates:
    duplicates_list.append([i, bldg_list.count(i)])

final_list = []
with da.SearchCursor(temp_isect_asc, fields) as cursor:
    prev_area = -1
    prev_item_list = []
    item_count = 0
    fcound = 0
    for row in cursor:
        if row[0] not in duplicates:
            final_list.append([row[0], row[1], row[2]])
        else:

            area = row[3] - row[4]
            index = duplicates.index(row[0])
            total_items = duplicates_list[index][1]
            if row[0] == duplicates[0] and item_count == 0:  # Deal with first item differently
                item_count += 1
                prev_area = area
                prev_item_list = [row[0], row[1], row[2]]
            elif item_count+1 == total_items:  # Deal with last item in list
                if prev_area <= area:
                    prev_area = area
                    prev_item_list = [row[0], row[1], row[2]]
                final_list.append(prev_item_list)
                item_count = 0
                prev_area = -1
                prev_item_list = []
            elif item_count+1 != total_items:
                if prev_area <= area:
                    prev_area = area
                    prev_item_list = [row[0], row[1], row[2]]
                item_count += 1

# Append results back to Input Feature Class
AddField(in_buildings, tile_fid, "LONG")
AddField(in_buildings, file_name, "TEXT")
with da.UpdateCursor(in_buildings, [building_fid, tile_fid, file_name]) as cursor:
    for r in cursor:
        for i in final_list:
            if r[0] == i[0]:
                r[1] = int(i[1])
                r[2] = str(i[2])
        cursor.updateRow(r)

Delete(temp_isect)
del bldg_list
del duplicates_list
del duplicates
