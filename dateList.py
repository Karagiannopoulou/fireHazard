# -*- coding: utf-8 -*-
# importing modules
import os, sys
import arcpy 
from arcpy import env
from arcpy.sa import *
import time
from datetime import date, timedelta
import numpy as np
import pandas as pd


# Check licenses 
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("3D")
#arcpy.env.overwriteOutput = True

#Start time
start_time = time.time()

#Set the variables
firePoints = r'D:\FireHazard\firepoints\centr_msg_date_wgs.shp'
maindir = r'Y:\data\KaterinaKarag\2018' 



def fireDates(input, firefield):
    dateList = []
    dateList_final = [] # the dates of fire events in the vector 
    
    with arcpy.da.SearchCursor(input, [firefield]) as cursor:
        
        for field in cursor:
            #print date 
            if field not in dateList: 
                        
                dateList.append(field)               
            
    for dates in dateList:
        if dates[0] != 'NaT':
            #intDateTime = datetime.datetime(intDates)
            dateList_final.append(dates[0])  
            
    #print ("Dates List from vector {}".format(dateList_final)) 
    return dateList_final 
    
def raster_info(input2,wildcard):
    HDF_info = []  # a list containing the raster names and the date  
    rasterDate = []
    
    for folderPath, folderNames, rasterFiles in os.walk(input2):
    
    #print folderPath
    
        for foldername in folderNames:
            
            
            inner_folderPath = os.listdir(os.path.join(folderPath,foldername))
            
#             print ("inner {}".format(inner_folderPath))
            
 
            
            for filename in inner_folderPath:
                
                
                if filename.endswith(wildcard):
                
                    # print .hdf files
                    HDF_info.append(filename)

                    # make the raster names
                    rasterNames = filename.rsplit('.',1)[0]
        
                    # isolate the dates from raster files
                    rasterDate = rasterNames.split('.',-1)[1]
                    rasterDate = rasterDate[1:]
                    
                    day_of_the_year = datetime.datetime.strptime(rasterDate,'%Y%j')
                    converted2datetime= day_of_the_year.strftime("%Y%m%d")
        
                    HDF_info.append(converted2datetime)
                
        return HDF_info 
            
def compare2lists(vectorDates, rasterInfo):
    
    # To vector array einai ta dates me tis fwties
    vector_array = np.sort(np.array(vectorDates))

    
    # Ta raster dates tha einai mia katheth lista me tis hmeromhnies to raster, kai ta filenames ta onomata 
    raster_dates=[]; fileNames = []

    for count, i in enumerate(rasterInfo):
        if count % 2 == 1:
            raster_dates.append(i)
        
        # edw me to mod, lew opou h thesh einai odd einai raster date kai opou zugh einai filename   
            
        elif count % 2 == 0:
            fileNames.append(i)
             
    raster_dates_array = np.vstack(np.array(raster_dates))   
    fileNames_array = np.vstack(np.array(fileNames)) 
    rasters_array = np.column_stack((raster_dates_array, fileNames_array))
    
    min_date = []  
    dates_dictionary = {}
    
    for firedate in vector_array:        
        for ndvi_dates in raster_dates_array[:,0]:
            
            if ndvi_dates < firedate:
 
                min_date.append(ndvi_dates) 
                prev_NDVI = max(min_date)
                 
                tmp = {}
                tmp[firedate] = prev_NDVI
                
                dates_dictionary.update(tmp)
            
   
    
    for keys, values in dates_dictionary.items():
        
        #print ("days {}".format(values)) 

        max_days_index = np.where(rasters_array[:,0] == values)
        max_fileNames = rasters_array[:,1][max_days_index]

        tmp2={}
        tmp2[keys] = values, max_fileNames
        
        dates_dictionary.update(tmp2)
        
        
#     print dates_dictionary
    return dates_dictionary 

def rastersProjection(dates_dictionary, directory):
    
    #walk = arcpy.da.Walk(directory, topdown = True)
    
    for keys, values in dates_dictionary.items():
        
        arrays_withnames = [arrays for  arrays  in values[1]]
         
         
        for hdf_file in arrays_withnames:
            
           
            for folderPath, folderNames, fileNames in os.walk(directory):
                
                for modis_images in fileNames:                       
                
                    if modis_images == hdf_file:
                        
#                         print ("hdf_file  {}".format(hdf_file))
#                         print ("modis_images  {}".format(modis_images))

                        workspace = env.workspace = folderPath
                        
                        raster_modis_images = arcpy.Raster(modis_images)
                        
                        print ("raster_modis_images {}".format(raster_modis_images))
                        
                        
                        # extract from hdf multiband layer the first band which is the NDVI and convert it to geotiff
                                                
                        try: 
                            ndvi_name = modis_images.split(".hdf")[0] + "_ndvi.tif"
                            ndvi_path = os.path.join(workspace, ndvi_name)
                            ndvi_image = arcpy.ExtractSubDataset_management(raster_modis_images,ndvi_path, "0")
                            
                            print ("ndvi_image  {}".format(ndvi_image))
                            
                            
                            # project ndvi images
                            
                            prj_name = modis_images.split(".hdf")[0] + "_prj.tif"
                            prj_path = os.path.join(workspace, prj_name)
                            prj_ndvi = arcpy.ProjectRaster_management(ndvi_image, prj_path, "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", "NEAREST", "5.59954171587093E-03 5.59954171587093E-03", "", "", "PROJCS['Unknown_datum_based_upon_the_custom_spheroid_Sinusoidal',GEOGCS['GCS_Unknown_datum_based_upon_the_custom_spheroid',DATUM['D_Not_specified_based_on_custom_spheroid',SPHEROID['Custom_spheroid',6371007.181,0.0]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Sinusoidal'],PARAMETER['false_easting',0.0],PARAMETER['false_northing',0.0],PARAMETER['central_meridian',0.0],UNIT['Meter',1.0]]", "NO_VERTICAL")
    
                            
                            print ("prj_ndvi  {}".format(prj_ndvi))
                            
                        except arcpy.ExecuteError:
                            #print(arcpy.GetMessages())
                            
                            continue
                            

def main():
    dates_from_vector = fireDates(firePoints, "firedate_g")
    rasterInfo = raster_info(maindir, '.hdf')
    dates_dictionary = compare2lists(dates_from_vector,rasterInfo)
    HDF_rasters = rastersProjection(dates_dictionary, maindir)
    

    #print ("values {}".format(dates_dictionary.values()))


if __name__ == "__main__":
    main()
    
     
arcpy.CheckInExtension('Spatial')    

elapsed_time = time.time() - start_time
print time.strftime("%H:%M:%S", time.gmtime(elapsed_time))  
