# -*- coding: utf-8 -*-
# importing modules
import os, sys
import arcpy 
from arcpy import env
from arcpy.sa import *
import time
from datetime import date

# Check licenses 
arcpy.CheckOutExtension("Spatial")
arcpy.CheckOutExtension("3D")
arcpy.env.overwriteOutput = True

#Start time
start_time = time.time()

#Set the variables
firePoints = r'D:\FireHazard\firepoints\centr_msg_date_wgs.shp'
maindir = r'D:\FireHazard\original_data_katerina' 

def fireDates(input, firefield):
    dateList = []
    dateList_final = []
    
    with arcpy.da.SearchCursor(input, [firefield]) as cursor:
        
        for field in cursor:
            #print date 
            if field not in dateList: 
                        
                dateList.append(field)               
            
    #print dateList
        
    for dates in dateList:
        if dates[0] != 'NaT':
            #intDateTime = datetime.datetime(intDates)
            dateList_final.append(dates[0])  
            
            #dateList_final = datetime(dateList_final)  
    
        
    print ("Dates List from vector {}".format(dateList_final))  
    
def raster_info(input,wildcard):
    HDF_info = []  # a list containing the raster names and the date  
    rasterDate = []
    
    
    for files in os.listdir(input):
        if files.endswith(wildcard):
            
            # print .hdf files
            HDF_info.append(files)
            
            #print ("HDF_rasterName {}".format(HDF_info)) 
            # make the raster names
            rasterNames = files.rsplit('.',1)[0]
     
            #print ("rasterNames {}".format(rasterNames))
            # isolate the dates from raster files
            rasterDate = rasterNames.split('.',-1)[1]
            rasterDate = rasterDate[1:]
            
            day_of_the_year = datetime.datetime.strptime(rasterDate,'%Y%j')
            
            converted2datetime= day_of_the_year.strftime("%Y%m%d")
            
            
 
            HDF_info.append(converted2datetime)
            
    print HDF_info
        



def main():
    dates_from_vector = fireDates(firePoints, "firedate_g")
    rasterInfo = raster_info(maindir, '.hdf')
        

if __name__ == "__main__":
    main()
     
arcpy.CheckInExtension('Spatial')    

elapsed_time = time.time() - start_time
print time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
   