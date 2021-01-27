####################################
#   File name: batch_export_tiled_models.py
#   About: Process for batch exporting multiplatch models that have been pre-attributed by tile_id.
#   Author: Geoff Taylor | Imagery & Remote Sensing Team | Esri
#   Date created: 01/21/2021
#   Date last modified: 01/26/2021
#   Python Version: 3.7
####################################

from arcpy.analysis import Select
from arcpy.management import CreateFileGDB, Delete, MakeFeatureLayer
from arcpy.conversion import MultipatchToCollada
from arcpy import da
from os import path, makedirs, walk, sep
import zipfile


# Begin Script

def make_boolean(in_value):
    # Ensure list folders text-based boolean input is converted to boolean
    if in_value.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh', 'bingo', 'dude']:
        return True
    else:
        return False


def process():
    def ensure_dir(file_path):
        directory = path.dirname(file_path)
        if not path.exists(directory):
            makedirs(directory)

    def zipper(in_list, out_file_path):
        out_file = '{0}.zip'.format(out_file_path)
        ensure_dir(out_file)
        with zipfile.ZipFile(out_file, 'w') as zipMe:
            for f in in_list:
                arcname = f.replace(path.dirname(out_file_path), "")
                zipMe.write(f, arcname=arcname, compress_type=zipfile.ZIP_DEFLATED)

    def zipper_gdb(in_gdb, out_file_name):
        assert in_gdb.endswith('.gdb'), "Error: file extension {0} not detected in in_folder".format(".gdb")
        root_dir = path.dirname(in_gdb)
        gdb_name = path.basename(in_gdb)
        myzip = zipfile.ZipFile(path.join(root_dir, out_file_name), 'w', zipfile.ZIP_DEFLATED)
        for folder, subfolder, file in walk(path.join(root_dir, gdb_name)):
            for each in subfolder + file:
                source = path.join(folder, each)
                if not source.endswith(".lock"):
                    # remove the absolute path to compose arcname
                    # also handles the remaining leading path separator with lstrip
                    arcname = source[len(root_dir):].lstrip(sep)
                    # write the file under a different name in the archive
                    myzip.write(source, arcname=arcname)
        myzip.close()

    def zip_folder(in_folder, out_file_name):
        myzip = zipfile.ZipFile(path.join(in_folder, out_file_name), 'w', zipfile.ZIP_DEFLATED)
        for folder, subfolder, file in walk(in_folder):
            for each in subfolder + file:
                source = path.join(folder, each)
                # remove the absolute path to compose arcname
                # also handles the remaining leading path separator with lstrip
                arcname = source[len(in_folder):].lstrip(sep)
                # write the file under a different name in the archive
                myzip.write(source, arcname=arcname)
        myzip.close()

    unique_values = set(row[0] for row in da.SearchCursor(in_buildings, tile_fid))
    for v in unique_values:
        print(v)

    for val in unique_values:
        out_name = out_file_basename + "_{0}".format(val)
        if out_format == "Multipatch SHP":
            out_file = path.join(out_folder, out_name+'.shp')
            Select(in_buildings, out_file, "FID_tiles = {0}".format(val))
            if zip_files:
                stem = path.join(out_folder, out_name)
                in_list = [out_file,
                           '{}.shp.xml'.format(stem),
                           '{}.shx'.format(stem),
                           '{}.sbx'.format(stem),
                           '{}.sbn'.format(stem),
                           '{}.prj'.format(stem),
                           '{}.dbf'.format(stem),
                           '{}.cpg'.format(stem)]
                zipper(in_list, stem)
                Delete(out_file)
        if out_format == "Multipatch GDB":
            gdb = path.join(out_folder, out_name + '.gdb')
            CreateFileGDB(out_folder, out_name + '.gdb')
            out_file = path.join(gdb, out_name)
            Select(in_buildings, out_file, "FID_tiles = {0}".format(val))
            if zip_files:
                out_zip = out_name + '.zip'
                zipper_gdb(gdb, out_zip)
                Delete(gdb)
        if out_format == "DAE":
            folder = path.join(out_folder, out_name)
            ensure_dir(folder)
            MakeFeatureLayer(in_buildings, "bldg_layer", "FID_tiles = {0}".format(val), None)
            MultipatchToCollada("bldg_layer", folder, "PREPEND_NONE", "OBJECTID")
            Delete("bldg_layer")
            if zip_files:
                zip_folder(folder, folder + ".zip")
                Delete(folder)


if __name__ == "__main__":
    debug = False
    if debug:
        # Input User Parameters
        in_buildings = r'C:\Users\geof7015\Documents\ArcGIS\Projects\Ohio_LiDAR_Demo\Ohio_LiDAR_Demo.gdb\Building_3D_manual'
        tile_fid = 'FID_tiles'
        out_format = "DAE"  # "Multipatch GDB", "Multipatch SHP", "DAE"
        zip_files = False
        out_folder = r'C:\Users\geof7015\Documents\ArcGIS\Projects\Ohio_LiDAR_Demo\test'
        out_file_basename = "bldg"
    else:
        from arcpy import GetParameterAsText
        in_buildings = GetParameterAsText(0)
        tile_fid = GetParameterAsText(1)
        out_format = GetParameterAsText(2)
        zip_files = make_boolean(GetParameterAsText(3))
        out_folder = GetParameterAsText(4)
        out_file_basename = GetParameterAsText(5)
    process()
