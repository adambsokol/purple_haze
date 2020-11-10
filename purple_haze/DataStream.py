'''
Module for the DataStream class.

A DataStream is a single dataset (corresponding to a single CSV file) produced by a sensor. The name Dataset was not used to avoid conflict with xarray Datasets.

There are, in theory, four DataStreams belonging to each Sensor instance:
    - Channel A primary
    - Channel A secondary
    - Channel B primary
    - Channel B secondary

Different "channels" are different wavelength lasers used to detect particles. Primary and Secondary datasets both have relevant informatoin (I'm still not sure as to why they are divded in two.)

A DataStream instance is initialiized with the file path for the stream's CSV file. 

'''

import re
import xarray as xr
import pandas as pd
import numpy as np

class DataStream:
    '''
    The DataStream class basically equates to a single CSV data file.
    Each purple air sensor should have four data streams (primary and secondary streams for two different channels)
    The class will contain some info about the stream (sensor name, )
    
    '''
    
    def __init__(self,filepath):


        """
        Initialization of the DataStream.
        
        Inputs:
            - filepath (string): path to a CSV file
            
        The DataStream is set up by parsing the file name for the relevant information:
            - loc: "inside", "outside", or "undefined" (all channel B streams are undefined)
            - sensor_name: name of the sensor that the stream belongs to
            - channel: "A" or "B"
            - data_type: 1 (primary dataset) or 2 (secondary) or 0 (unknown)
            - lat/lon: sensor coordinates
    
            
        The Purple Air CSV files have form:
        
        STATION NAME channel (loc) (lat lon) DataType 60_minute_average startdate enddate.csv 
        
        where startdate and enddate mark the time period for which the data was originally requested (so they should all be the same for this project)
        """
        
        self.filepath = filepath #full file path
        
        self.filename = filepath.split('./data/purple_air/')[1] # file name
        
        
        # first find the station location (inside, outside, or undefined)
        loc_options = ["(inside)", "(outside)", "(undefined)"]
        
        #loop through the three location options
        found_loc = False
        
        for loc_option in loc_options: 
            
            if loc_option in self.filename.lower(): #found location
                
                self.loc = loc_option[1:-1] #removes the parenthesis
                name, data_info = self.filename.split(loc_option) #sensor name comes before location; data info comes after
                self.sensor_name = name.strip() #station name is everything before the location
                
                
                ### Get channel (A or B; only channel B files have the channel in the file name)
                if self.sensor_name.endswith(' B'): 
                    self.channel = 'B'
                    self.sensor_name = self.sensor_name[:-1].strip().lower() #remove the channel from the sensor name
                else: 
                    self.channel = 'A'
                    self.sensor_name = self.sensor_name.lower() #make lowercase
                    
                    
                ### Determine data type
                if 'Primary' in data_info:
                    self.data_type = 1 #primary 
                elif 'Secondary' in data_info:
                    self.data_type = 2 #secondary 
                else:
                    self.data_type = 0 #unknown
                        
                
                ### Get lat/lon coordinates
                latlon_pattern = r'\([0-9]+.[0-9]+ [-]+[0-9]+.[0-9]+\)' #regex search pattern for lat/lon coordinates separated by a space
                search_result = re.search(latlon_pattern, data_info) #search the file name
                
                if search_result: #found coordinates
                    latlon_string = search_result.group()[1:-1] #removes parenthesis
                    lat_string, lon_string = latlon_string.split() #separate lat/lon
                    self.lat = float(lat_string)
                    self.lon = float(lon_string)
                else: # did not find coordinates
                    raise ValueError("Could not determine sensor coordinates from the file name.")
                
                found_loc = True
                
                break
                
        if not found_loc:
            raise ValueError("Could not determine sensor location (inside/outside/undefined) from file name.")
                

                
                
                
    
    def load(self):
        '''
        Read in the CSV file for the Data Stream
        '''
        # read into an xarray dataset
        ds = xr.Dataset.from_dataframe(pd.read_csv(self.filepath, index_col='created_at'))
                
        #drop some unneeded/artifact fields
        dropvars = ['Unnamed: 9', 'RSSI_dbm', 'IAQ', 'ADC']
        
        for dropvar in dropvars:
            if dropvar in ds:
                ds = ds.drop(dropvar)
            else:
                pass
        
        
        # lets make some friendlier names for the data fields
        rename = {'created_at':'time',
                  'Pressure_hpa': 'pressure',
                  'PM1.0_CF1_ug/m3': 'pm1_cf1',
                  'PM2.5_CF1_ug/m3': 'pm25_cf1',
                  'PM10.0_CF1_ug/m3': 'pm10_cf1',
                  '>=0.3um/dl': 'n_pm03',
                  '>=0.5um/dl': 'n_pm05',
                  '>1.0um/dl': 'n_pm1',
                  '>=2.5um/dl': 'n_pm25',
                  '>=5.0um/dl': 'n_pm5',
                  '>=10.0um/dl': 'n_pm10',
                  'PM2.5_ATM_ug/m3': 'pm25_atm',
                  'PM1.0_ATM_ug/m3': 'pm1_atm',
                  'PM10_ATM_ug/m3': 'pm10_atm',
                  'UptimeMinutes': 'uptime',
                  'Temperature_F': 'temp',
                  'Humidity_%': 'rh'}
        
        # if we have Channel B data, let's add that to the dataset variable names
        #if self.channel == 'B':
        #    for key in rename.keys():
        #        if key != 'created_at' and key != 'Pressure_hpa': #Pressure field is only in channel B data
        #            rename[key] = rename[key]+'b'
        
        #loop through and rename the variables
        for old_name, new_name in rename.items():
            if old_name in ds:
                ds = ds.rename({old_name: new_name})
            else:
                pass
        
        
        # lets assign some units
        ug_m3 = ['pm1', 'pm25', 'pm10', 'pm25_atm', 'pm1_atm', 'pm10_atm']
        per_dl = ['pm03_n', 'pm05_n', 'pm10_n', 'pm25_n', 'pm50_n', 'pm100_n']
        
        for field in ds.keys():
            if field in ug_m3:
                ds[field].attrs['units'] = 'ug/m3'
            elif field in per_dl:
                ds[field].attrs['units'] = '/dl'
            elif field == 'temp':
                ds[field].attrs['units'] = 'F'
            elif field == 'pressure':
                ds[field].attrs['units'] = 'hpa'
            elif field == 'rh':
                ds[field].attrs['units'] = '%'
            else:
                pass
                
        # convert the time field to datetimes
        time = ds.time.values
        time = np.array([pd.to_datetime(t) for t in time])
        ds['time'] = (('time'), time)

        # add some attributes with the DataStream info
        ds.attrs['sensor_name'] = self.sensor_name
        ds.attrs['channel'] = self.channel
        ds.attrs['loc'] = self.loc
        ds.attrs['data_type'] = self.data_type

        
        return ds