####################################
#   File name: batch_project_elevation.py
#   About: Process for batch converting elevation raster tiles.
#   Author: Geoff Taylor | Imagery & Remote Sensing Team | Esri
#   Date created: 01/25/2021
#   Date last modified: 01/25/2021
#   Python Version: 3.7
####################################

from arcpy.management import ProjectRaster, ExportMosaicDatasetPaths, Delete, AddRastersToMosaicDataset
from arcpy import da, CheckOutExtension, CheckInExtension, Describe, SpatialReference, AddError, AddMessage
from arcpy import env
from arcpy.ia import Times
from os.path import join, split, exists
from os import makedirs

env.overwriteOutput = True


def unitsCalc(inFeature):
    SpatialRef = arcpy.Describe(inFeature).spatialReference
    obtainunits = SpatialRef.linearUnitName
    try:
        if obtainunits == "Foot_US":
            units = "Foot"
            return units
        if obtainunits == "Foot":
            units = "Foot"
            return units
        if obtainunits == "Meter":
            units = "Meter"
            return units
        if obtainunits not in ["Foot_US", "Foot", "Meter"]:
            AddError("Units Not Detected on {0} \n Terminating Process".format(inFeature))
            exit()
    except:
        AddError("Units Not Detected on {0} \n Terminating Process".format(inFeature))
        exit()


def getCellFactor(inFeature):
    if unitsCalc(inFeature) == 'Foot':
        return 1
    else:
        return 0.3048


def createMosaics(gdb, mosaicName, folder, spatialRef, pixel_type):
    # Create mosaic dataset
    arcpy.CreateMosaicDataset_management(gdb, mosaicName, spatialRef, None, pixel_type, "CUSTOM", None)
    mosaicDS = join(gdb, mosaicName)
    AddMessage('Mosaic dataset {} created...'.format(mosaicName))

    # Add rasters to mosaic and set cell size
    AddMessage('Adding rasters to mosaic dataset...')
    AddRastersToMosaicDataset(mosaicDS, "Raster Dataset", folder, "UPDATE_CELL_SIZES",
                                               "UPDATE_BOUNDARY", "NO_OVERVIEWS", None, 0, 1500, None, '',
                                               "SUBFOLDERS", "ALLOW_DUPLICATES", "BUILD_PYRAMIDS",
                                               "CALCULATE_STATISTICS", "NO_THUMBNAILS", '',
                                               "NO_FORCE_SPATIAL_REFERENCE", "ESTIMATE_STATISTICS", None,
                                               "NO_PIXEL_CACHE")
    # Update mosaic cell size
    arcpy.AddMessage('Updating mosaic cell size...')
    cellSize = arcpy.GetRasterProperties_management(mosaicDS, "CELLSIZEX")
    newSize = float(float(cellSize.getOutput(0))/2)
    arcpy.SetMosaicDatasetProperties_management(mosaicDS, cell_size=newSize)

    # Add results to the display
    arcpy.AddMessage('Adding results to map views...')
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    for m in aprx.listMaps():
        if m.mapType == "MAP":
            m.addDataFromPath(mosaicDS)


def process():
    # Detect Unit of Measurement (Feet -vs- Meter)
    cell_factor = getCellFactor(in_mosaic_dataset)

    # Obatin List of Raster Files in Mosaic Dataset
    temp_table = join("memory", "temp_table")
    ExportMosaicDatasetPaths(in_mosaic_dataset, temp_table, "#", "ALL", "RASTER")
    rasters = set(row[0] for row in da.SearchCursor(temp_table, "Path"))
    Delete(temp_table)

    if not exists(out_directory):
        makedirs(out_directory)

    # Process each raster
    for in_raster in rasters:
        root_dir, file = split(in_raster)
        AddMessage("da filename is: {}".format(file))
        out_raster = join(out_directory, file)

        desc = Describe(in_raster)
        cell_size_height = desc.children[0].meanCellHeight  # Cell size in the Y axis and / or
        cell_size_width = desc.children[0].meanCellWidth  # Cell size in the X axis
        cell_size = "{0} {1}".format(cell_size_height*cell_factor, cell_size_width*cell_factor)

        if unitsCalc(in_mosaic_dataset) == "Foot":
            outTimes = Times(in_raster, 0.3048)
            ProjectRaster(in_raster=outTimes,
                          out_raster=out_raster,
                          out_coor_system=out_spatial_reference,
                          resampling_type=resampling_type,
                          cell_size=cell_size,
                          geographic_transform=geographic_transform,
                          in_coor_system=input_spatial_reference)
        else:
            ProjectRaster(in_raster=in_raster,
                          out_raster=out_raster,
                          out_coor_system=out_spatial_reference,
                          resampling_type=resampling_type,
                          cell_size=cell_size,
                          geographic_transform=geographic_transform,
                          in_coor_system=input_spatial_reference)

    # Delete Intermediate Data
    del rasters
    if out_mosaic_dataset:
        root_dir, file = split(out_mosaic_dataset)
        # TODO: Automatically detect Pixel Type from input Mosaic Dataset Rasters and pass below
        createMosaics(root_dir, file, out_directory, out_spatial_reference, "32_BIT_UNSIGNED")


if __name__ == "__main__":
    debug = False
    if debug:
        # Set local variables
        in_mosaic_dataset = r'C:\Users\geof7015\Documents\ArcGIS\Projects\Leveraging_LiDAR\scratch\SurfaceRasters\SurfaceMosaics.gdb\DTM'
        resampling_type = "BILINEAR"  # "NEAREST", "BILINEAR", "CUBIC", "MAJORITY"
        input_spatial_reference = ""
        out_spatial_reference_string = "WGS 1984"
        geographic_transform = "NAD_1983_To_WGS_1984_5"
        file_extension = "tif"
        out_directory = r''
        out_mosaic_dataset = r''
        # System Parameters
        out_spatial_reference = SpatialReference(out_spatial_reference_string)
    else:
        from arcpy import GetParameterAsText
        in_mosaic_dataset = GetParameterAsText(0)

        input_spatial_reference = arcpy.SpatialReference()
        input_spatial_reference.loadFromString(GetParameterAsText(1))

        out_spatial_reference = arcpy.SpatialReference()
        out_spatial_reference.loadFromString(GetParameterAsText(2))

        geographic_transform = GetParameterAsText(3)
        resampling_type = GetParameterAsText(4)
        file_extension = GetParameterAsText(5)
        out_directory = GetParameterAsText(6)
        out_mosaic_dataset = GetParameterAsText(7)

        AddMessage(input_spatial_reference)
        AddMessage(out_spatial_reference)
    process()
