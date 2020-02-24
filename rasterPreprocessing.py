# -*- coding: utf-8 -*-
# importing modules
import os, sys
import arcpy
from arcpy import env
from arcpy.sa import *
from arcpy.da import *
import time
from datetime import date, timedelta
from datetime import datetime as dt
from datesDictionary import fireDates
from datesDictionary import raster_info
from datesDictionary import compare2lists

# Check licenses
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("3D")
arcpy.env.overwriteOutput = True

# Set up global variables
maindir = r'Y:\data\KaterinaKarag\2018'
firePoints = r'D:\FireHazard\firepoints\centr_msg_date_wgs.shp'

# Start time
start_time = time.time()


def rastersPreprocessing(dates_dictionary, directory):
    for keys, values in dates_dictionary.items():


        arrays_withnames = [arrays for arrays in values[1]]

        for hdf_file in arrays_withnames:

            for folderPath, folderNames, fileNames in os.walk(directory):

                for modis_images in fileNames:

                    if modis_images == hdf_file:

                        workspace = env.workspace = folderPath

                        raster_modis_images = arcpy.Raster(modis_images)


                        try:
                            # Extract ndvi layer from hdf multiband
                            ndvi_name = modis_images.split(".hdf")[0] + "_ndvi.tif"
                            ndvi_path = os.path.join(workspace, ndvi_name)
                            ndvi_image = arcpy.ExtractSubDataset_management(raster_modis_images, ndvi_path, "0")

                            print("ndvi_image  {}".format(ndvi_image))

                            # project ndvi images
                            prj_name = modis_images.split(".hdf")[0] + "_prj.tif"
                            prj_path = os.path.join(workspace, prj_name)
                            prj_ndvi = arcpy.ProjectRaster_management(ndvi_image, prj_path,
                                                                      "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]",
                                                                      "NEAREST",
                                                                      "5.59954171587093E-03 5.59954171587093E-03", "",
                                                                      "",
                                                                      "PROJCS['Unknown_datum_based_upon_the_custom_spheroid_Sinusoidal',GEOGCS['GCS_Unknown_datum_based_upon_the_custom_spheroid',DATUM['D_Not_specified_based_on_custom_spheroid',SPHEROID['Custom_spheroid',6371007.181,0.0]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Sinusoidal'],PARAMETER['false_easting',0.0],PARAMETER['false_northing',0.0],PARAMETER['central_meridian',0.0],UNIT['Meter',1.0]]",
                                                                      "NO_VERTICAL")

                            print ("prj_ndvi  {}".format(prj_ndvi))

                        except arcpy.ExecuteError:
                            print(arcpy.GetMessages())

                            continue


def main():
    dates_from_vector = fireDates(firePoints, "firedate_g")
    rasterInfo = raster_info(maindir, '.hdf')
    dates_dictionary = compare2lists(dates_from_vector, rasterInfo)
    ndviPreprocessing = rastersPreprocessing (dates_dictionary, maindir)

if __name__ == "__main__":
    main()
  
arcpy.CheckInExtension('Spatial')

elapsed_time = time.time() - start_time
print (time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))                          