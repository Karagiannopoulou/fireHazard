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
import numpy as np

# Check licenses
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("3D")
arcpy.env.overwriteOutput = True


def fireDates(input, firefield):
    dateList = []
    dateList_final = []  # the dates of fire events in the vector

    with arcpy.da.SearchCursor(input, [firefield]) as cursor:

        for field in cursor:

            # append to a new list only the unique dates.

            if field not in dateList:
                dateList.append(field)

    for dates in dateList:
        if dates[0] != 'NaT':
            # intDateTime = datetime.datetime(intDates)
            dateList_final.append(dates[0])

            # print ("Dates List from vector {}".format(dateList_final))
    return dateList_final


def raster_info(input2, wildcard):
    HDF_info = []  # a list containing the raster names and the date
    rasterDate = []

    for folderPath, folderNames, rasterFiles in os.walk(input2):

        for foldername in folderNames:

            inner_folderPath = os.listdir(os.path.join(folderPath, foldername))

            #             print ("inner {}".format(inner_folderPath))

            for filename in inner_folderPath:

                if filename.endswith(wildcard):
                    # print .hdf files
                    HDF_info.append(filename)

                    # make the raster names
                    rasterNames = filename.rsplit('.', 1)[0]

                    # isolate the dates from raster files
                    rasterDate = rasterNames.split('.', -1)[1]
                    rasterDate = rasterDate[1:]

                    day_of_the_year = dt.strptime(rasterDate, '%Y%j')
                    converted2datetime = day_of_the_year.strftime("%Y%m%d")

                    HDF_info.append(converted2datetime)

        return HDF_info


def compare2lists(vectorDates, rasterInfo):
