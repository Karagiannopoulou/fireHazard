# -*- coding: utf-8 -*-
# importing modules
import os, sys
import arcpy
from arcpy import env
from arcpy.sa import *
import time
from datetime import date, timedelta
import numpy as np
from datesDictionary import fireDates
from datesDictionary import raster_info
from datesDictionary import compare2lists

# Check licenses
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("3D")
arcpy.env.overwriteOutput = True

# Start time
start_time = time.time()

# Set up global variables
maindir = r'Y:\data\KaterinaKarag\2018'
firePoints = r'D:\FireHazard\firepoints\centr_msg_date_wgs.shp'
fc_schema = r'C:\Users\noa\eclipse-workspace\ZonalStatistics\output\fc_schema.shp' # standardized shapefile's schema (attribute table),which will denote empty's shapefile schema. 
output_folder = r'C:\Users\noa\eclipse-workspace\ZonalStatistics\output' # setup where you want to save the output shapefile with the ndvi values. 


# call build-in functions


# create an empty shape file to be filled with the ndvi values
def emptyFC(firePoints, default_schema):
    try:
        outputname = 'fc_ndvi.shp'
        spatial_ref = arcpy.Describe(firePoints).spatialReference
        emptyFC = arcpy.CreateFeatureclass_management(output_folder, outputname, "POINT", default_schema, "DISABLED", "DISABLED", spatial_ref)
         
         
    except:
        print arcpy.GetMessages() 
    
    return emptyFC


def zonalndvi(emptyFC, dictionary):  

    for keys, values in dictionary.items():
        
    
        img01 = str(values[1][0].split(".hdf")[0]) + "_prj.tif"
        img02 = str(values[1][1].split(".hdf")[0]) + "_prj.tif"
        img03 = str(values[1][2].split(".hdf")[0]) + "_prj.tif"
        
        
        name1 = img01[17:23]
        name2 = img02[17:23]
        name3 = img03[17:23]                  
    
        try:
            arcpy.MakeFeatureLayer_management(firePoints,"firePoints_lyr")
            query = """ "firedate_g" = '%s'"""%keys
            
            print(query)
            
            arcpy.SelectLayerByAttribute_management("firePoints_lyr", "NEW_SELECTION", query)
            
            
            for folderPath, folderNames, fileNames in os.walk(maindir):
                
                for prj_images in fileNames:
                    
                    
                    if prj_images == img01:
                        
                        workspace = env.workspace = folderPath
                        raster_images = arcpy.Raster(prj_images)                 
                        
                        outputName1 = "fc_" + keys + name1 + '.shp'
                        
     
                        extracted_vector1 = os.path.join(output_folder, outputName1) 
                        arcpy.gp.ExtractValuesToPoints_sa("firePoints_lyr", raster_images, extracted_vector1, "NONE", "VALUE_ONLY")
                        
                        print("extracted vector1 {}".format(extracted_vector1))
    
                        arcpy.Append_management(extracted_vector1 ,emptyFC,'TEST')
                        
                        
                        arcpy.Delete_management(extracted_vector1)
    
                        
                    if prj_images == img02:
                        
                        workspace = env.workspace = folderPath
                        raster_images = arcpy.Raster(prj_images)
                        
                        
                        outputName2 = "fc_" + keys + name2 + '.shp'
                        
                        extracted_vector2 = os.path.join(output_folder, outputName2)
                        
                        arcpy.gp.ExtractValuesToPoints_sa("firePoints_lyr", raster_images, extracted_vector2, "NONE", "VALUE_ONLY")
                        
                        print("extracted vector2 {}".format(extracted_vector2))
    
                        arcpy.Append_management(extracted_vector2, emptyFC,'TEST')
                        
                        arcpy.Delete_management(extracted_vector2)
                        
                        
                    if  prj_images == img03:
                        
                        workspace = env.workspace = folderPath
                        raster_images = arcpy.Raster(prj_images)
                        
                        outputName3 = "fc_" + keys + name3 + '.shp'
                        extracted_vector3 = os.path.join(output_folder, outputName3)
                        
                        arcpy.gp.ExtractValuesToPoints_sa("firePoints_lyr", raster_images, extracted_vector3, "NONE", "VALUE_ONLY")
                        
                        print("extracted vector3 {}".format(extracted_vector3))
                        
                        arcpy.Append_management(extracted_vector3 ,emptyFC,'TEST')
                        
                        arcpy.Delete_management(extracted_vector3)

            
        except:
            print arcpy.GetMessages()
            
            
            
                
    return  emptyFC   
        

 
def main():
    dates_from_vector = fireDates(firePoints, "firedate_g")
    rasterInfo = raster_info(maindir, '.hdf')
    dates_dictionary = compare2lists(dates_from_vector, rasterInfo)
    emptyFC = emptyFC(firePoints, fc_schema)
    FC_withNDVI = zonalndvi(emptyFC, dates_dictionary)
    

 
if __name__ == "__main__":
    main()

arcpy.CheckInExtension('Spatial')

elapsed_time = time.time() - start_time
print (time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
