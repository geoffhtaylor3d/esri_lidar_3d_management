from collada import *
from os.path import exists, dirname, join
import xml.etree.ElementTree as ET
from decimal import Decimal

#in_file = r'C:\Users\geof7015\Documents\GitHub\esri_lidar_3d_management\sample_data\ID_6.dae'
in_file = r'C:\Users\geof7015\Documents\GitHub\esri_lidar_3d_management\sample_data\ID_6.kml'

file_type = "kml"  # "kml", "dae"


def get_kml_info(in_kml_file):
    tree = ET.parse(in_kml_file)
    root = tree.getroot()
    name = ""
    longitude = ""
    latitude = ""
    altitude = ""
    scale_x = ""
    scale_y = ""
    scale_z = ""
    file_path = ""
    for line in root.iter('*'):
        if str(line.tag).endswith("name"):
            name = line.text
        if str(line.tag).endswith("longitude"):
            longitude = Decimal(line.text)
        if str(line.tag).endswith("latitude"):
            latitude = Decimal(line.text)
        if str(line.tag).endswith("altitude"):
            altitude = Decimal(line.text)
        if str(line.tag).endswith("x"):
            scale_x = Decimal(line.text)
        if str(line.tag).endswith("y"):
            scale_y = Decimal(line.text)
        if str(line.tag).endswith("z"):
            scale_z = Decimal(line.text)
        if str(line.tag).endswith("href"):
            file_path = line.text
    coords = [latitude, longitude, altitude]
    scale = [scale_x, scale_y, scale_z]
    return [name, file_path, coords, scale]


def read_dae(in_dae_file):
    tree = ET.parse(in_dae_file)
    root = tree.getroot()
    for line in root.iter('*'):
        print(line)
        if str(line.tag).endswith("name"):
            '''
            'COLLADA'
            'asset'
            'created'
            'modified'
            'up_axis'
            'library_geometries'
            'geometry'
            'mesh'
            'source'
            '''
        if str(line.tag).endswith("float_array"):
            print(line.text)
            'float_array'
            '''
            'technique_common'
            'accessor'
            'param'
            'param'
            'param'
            'source'
            'float_array'
            'technique_common'
            'accessor'
            'param'
            'param'
            'param'
            'vertices'
            'input'
            'triangles'
            'input'
            'input'
            '''
        if str(line.tag).endswith("p"):
            print(line.text)
            '''
            'library_effects'
            'effect'
            'profile_COMMON'
            'technique'
            'phong'
            'diffuse'
            'color'
            'library_materials'
            'material'
            'instance_effect'
            'library_visual_scenes'
            'visual_scene'
            'node'
            'translate'
            'instance_geometry'
            'bind_material'
            'technique_common'
            'instance_material'
            'scene'
            'instance_visual_scene'
            '''
        print(line)


if file_type == "kml":
    assert exists(in_file) and in_file.endswith(".kml"), \
        "Detected that File: {0} does not exist or file is not kml format".format(in_file)
    name, file_path, coords, scale = get_kml_info(in_file)
    print(name, file_path, coords, scale)
    dae_file = join(dirname(in_file), name)
    print(dae_file)
    read_dae(dae_file)

if file_type == "dae":
    assert exists(in_file) and in_file.endswith(".dae"), \
        "Detected that File: {0} does not exist or file is not dae format".format(in_file)
    print("model dows not contain positional information for georegistration")
    read_dae(in_file)
