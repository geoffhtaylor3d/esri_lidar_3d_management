from arcpy import ListTransformations, Describe, SpatialReference, Extent


class ToolValidator:
    # Class to add custom behavior and properties to the tool and tool parameters.

    # More info: https://pro.arcgis.com/en/pro-app/latest/arcpy/geoprocessing_and_python/programming-a-toolvalidator-class.htm
    # More info 1: https://pro.arcgis.com/en/pro-app/latest/arcpy/geoprocessing_and_python/customizing-script-tool-behavior.htm

    def list_transformations(self, in_mosaic_dataset, in_spatial_reference, to_spatial_reference):
        desc_mosaic = Describe(in_mosaic_dataset)
        xmin = desc_mosaic.extent.XMin
        xmax = desc_mosaic.extent.XMax
        ymin = desc_mosaic.extent.YMin
        ymax = desc_mosaic.extent.YMax
        extent = Extent(xmin, xmax, ymin, ymax)
        # in_sr = Describe(in_mosaic_dataset).spatialReference
        in_sr = in_spatial_reference
        out_sr = to_spatial_reference
        # out_sr = arcpy.SpatialReference(to_spatial_reference)
        # out_sr = arcpy.SpatialReference()
        # out_sr = out_sr.loadFromString(to_spatial_reference)
        return ListTransformations(in_sr, out_sr, extent)

    def __init__(self):
        # set self.params for use in other function
        self.params = arcpy.GetParameterInfo()

    def initializeParameters(self):
        # Customize parameter properties.
        # This gets called when the tool is opened.
        self.params[1].enabled = False
        self.params[2].enabled = False
        self.params[3].enabled = False
        return

    def updateParameters(self):
        # Modify parameter values and properties.
        # This gets called each time a parameter is modified, before
        # standard validation.
        if self.params[0].value:
            self.params[1].enabled = True
            self.params[1].value = Describe(self.params[0]).spatialReference
            if self.params[1].value:
                self.params[2].enabled = True
                if self.params[2].value:
                    self.params[3].enabled = True
                    transformations = self.list_transformations(self.params[0].value, self.params[1].value,
                                                                self.params[2].value)
                    # self.params[3].value = transformations[0]
                    self.params[3].filter.list = transformations
        return

    def updateMessages(self):
        # Customize messages for the parameters.
        # This gets called after standard validation.
        self.params[3].clearMessage()
        if self.params[3].value == "[]":
            self.params[3].value.setErrorMessage("Error: No Available Transformations Detected...Choose another projection")
        return

    # def isLicensed(self):
    #     # set tool isLicensed.
    #     return True
