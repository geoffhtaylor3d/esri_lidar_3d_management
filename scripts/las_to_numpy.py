####################################
#   File name: las_to_numpy.py
#   About: Process for iteratively converting las tiles to numpy arrays for processing
#   Author: Geoff Taylor | Imagery & Remote Sensing Team | Esri
#   Date created: 02/03/2021
#   Date last modified: 02/03/2021
#   Python Version: 3.7
####################################

from arcpy.management import Delete, MultipartToSinglepart
from arcpy import Exists, da, CheckExtension, CheckOutExtension, CheckInExtension, ExecuteError, GetMessages, \
    AddMessage, AddError
from arcpy.ddd import LASToMultipoint
from os.path import join, splitext
import arcpy.da
from os import listdir
import numpy as np


def array_2d_to_3d(in_2d_array):
    return np.array([[x for x in y] for y in in_2d_array])


def esri_numpy_operation_here(lidar_points):
    AddMessage('detected {} points in numpy array'.format(lidar_points.size))
    print("first 10 rows in numpy array")
    print(lidar_points[:10])
    print("Data Type: {}".format(type(lidar_points)))
    print("Array Shape: {)".format(lidar_points.shape))
    print("Array Number of Dimensions: {}".format(lidar_points.ndim))

    # Convert values from 8-bit points to 64-bit points for processing in scikit
    pts_64 = lidar_points.view(np.float64).reshape(lidar_points.shape + (-1,))

    # Example of running scikit learn
    # Implement one of the following algorithms
    # https://scikit-learn.org/stable/modules/generated/sklearn.cluster.OPTICS.html  # sklearn.cluster.OPTICS
    # https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html  # sklearn.cluster.DBSCAN
    from sklearn.cluster import OPTICS
    dist = 10
    mimumum_samples = 4
    clustering = OPTICS(min_samples=mimumum_samples, max_eps=dist, n_jobs=-1).fit(pts_64)
    print(clustering.labels_[:200])


def las_tile_to_numpy(lidar_tile, sr, returns, class_codes):
    temp_lasd = "{0}_temp.lasd".format(splitext(lidar_tile)[0])
    if Exists(temp_lasd):
        Delete(temp_lasd)
    arcpy.CreateLasDataset_management(lidar_tile, temp_lasd, spatial_reference=sr)
    point_spacing = arcpy.Describe(temp_lasd).pointSpacing
    Delete(temp_lasd)

    temp_pts_multi = join("in_memory", "temp_pts_multi")
    if Exists(temp_pts_multi):
        Delete(temp_pts_multi)
    LASToMultipoint(input=lidar_tile,
                    out_feature_class=temp_pts_multi,
                    average_point_spacing=point_spacing,
                    class_code=class_codes,
                    _return=returns,
                    input_coordinate_system=sr)

    lidar_points = da.FeatureClassToNumPyArray(in_table=temp_pts_multi,
                                               # field_names=["OID@", "SHAPE@X", "SHAPE@Y", "SHAPE@Z"],
                                               field_names=["SHAPE@X", "SHAPE@Y", "SHAPE@Z"],
                                               # field_names=["SHAPE@XYZ"],
                                               spatial_reference=sr,
                                               explode_to_points=True)
    Delete(temp_pts_multi)

    # Numpy Processing Operation Goes Here!
    esri_numpy_operation_here(lidar_points)

    del lidar_points


def las_tiles_to_numpy(in_lidar_folder, sr, lidar_format, returns, class_codes):
    class LicenseError(Exception):
        pass

    try:
        if CheckExtension("3D") == "Available":
            CheckOutExtension("3D")
        else:
            # raise a custom exception
            raise LicenseError

        if not lidar_format.startswith("."):  # Ensure lidar format contains a format decimal
            lidar_format = ".{}".format(lidar_format)
        supported_lidar_formats = [".las", ".zlas"]
        assert lidar_format in supported_lidar_formats, \
            "LiDAR format {0} unsupported. Ensure LiDAR format is in {1}".format(lidar_format, supported_lidar_formats)

        lidar_tiles = [f for f in listdir(in_lidar_folder) if f.endswith("{}".format(lidar_format))]
        if len(lidar_tiles) < 1:
            AddError("No LiDAR tiles detected in input directory")
        count = 0
        for tile in lidar_tiles:
            AddMessage("processing lidar tile {0} of {1} : {2}".format(count+1, len(lidar_tiles), tile))
            lidar_tile = join(in_lidar_folder, tile)
            las_tile_to_numpy(lidar_tile, sr, returns, class_codes)
            count += 1
        AddMessage("processing {} lidar tiles complete".format(count))

        # Check back in 3D Analyst license
        CheckInExtension("3D")
    except LicenseError:
        AddError("3D Analyst license is unavailable")
    except ExecuteError:
        AddError("3D Analyst license is unavailable")
        print(GetMessages(2))


if __name__ == "__main__":
    # Input User Parameters
    in_lidar_folder = r'C:\Users\geof7015\Documents\ArcGIS\Projects\LiDAR_Test\las_thinned_1m'
    srXY = 6347
    srZ = 115755
    lidar_format = "las"
    returns = "ANY_RETURNS"
    class_codes = [5]

    # System Parameters + Script
    sr = arcpy.SpatialReference(srXY, srZ)
    las_tiles_to_numpy(in_lidar_folder, sr, lidar_format, returns, class_codes)
