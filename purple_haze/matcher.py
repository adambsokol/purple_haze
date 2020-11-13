'''Function to match PurpleAir sensors to SES data. Also loads SES data.
To run do the following commands (as of 11/13):

import air as air
import matcher as match
sensor_data = air.files_to_dataframe(glob.glob('../data/purple_air/*'))
matched_ses_data = match.station_matcher(real_data)

Note, you may have to change the imports depending on where you're running this from. If you are in the purple_haze folder this works.
'''


import geopandas as gpd
from geopandas.tools import sjoin
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def get_sensor_names(data_array , name10):
    '''This is a helper function that grabs the sensors in each census tract from the joined dataframe to append to the SES data
    If there are no sensors in a census tract it returns a nan.
    '''
    try:
        return data_array['all_names'][name10]
    except:
        return np.nan


def station_matcher(lat_lons):
    '''This function will take in a dataframe that has the sensor file name, its lat, its lon, and possibly other stuff.
    It will then load in the SES data and match the purple air files to their respective census tract.
    Ultimately, it will return the SES data with a new column that is a list of the filenames of all Purple air stations in that census
    tract.
    
    '''
    
    ses_file = '../data/Seattle_ses_data/ses_data.shp'
    ses_data = gpd.read_file(ses_file)
    #Converting it to what is the default lat/lon format
    new_ses_data = ses_data.to_crs(epsg=4326)
    
    #Assume that the sensors lat/lon are in a Pandas Dataframe with columns of Lat and Lon
    #We will then convert it to a GeoDataFrame
    sensor_gdf = gpd.GeoDataFrame(lat_lons, geometry=gpd.points_from_xy(lat_lons['lon'], lat_lons['lat']), crs="EPSG:4326")
    
    #Combine them with INNER!!! This retains the sensor file names
    combined = sjoin(new_ses_data, sensor_gdf, how='inner', op='intersects')
    
    #Now we need to combine rows that have multiple entries
    #This 'NAME10' should be one unique name for each census tract. There are others too.
    grouped=combined.groupby('NAME10')
    
    #Make a new column called all_names that is a list of the names of each sensor seperated by commas
    #Note we could use an identifier for the sensors other than sensor name if we want
    #Would need to change the column='file' line if we wanted to do so
    aggregate=grouped.agg(all_names=pd.NamedAgg(column='file', aggfunc=','.join))
    
    #This is adding a new column to the original ses data that is called sensor_names
    #It has the same data that is in aggregate, but we have to do it this funny way I think (?)
    #Basically it goes row by row and uses our helper function (get_sensor_names) to grab the sensor names from aggregate
    new_ses_data['sensor_file_names'] = new_ses_data.apply(lambda row: get_sensor_names(aggregate , row['NAME10']), axis=1)

    return new_ses_data
    