'''
air module of the purple_haze package.

Contains class definitions for the Sensor and DataStream classes as well as some functions. 
'''



import re
import xarray as xr
import pandas as pd
import numpy as np






################################################################################
################################## Functions ###################################
################################################################################


def files_to_dataframe(file_list):
    '''
    This function creates a pandas dataframe with one row for each file in the input file_list and one column for each of the default attributes of the DataStream class.
    '''
    
    # convert file names to list of DataStream objects
    data_streams = [DataStream(file) for file in file_list]
    
    # make dataframe
    df = pd.DataFrame({'file': file_list,
                      'lat': [stream.lat for stream in data_streams],
                      'lon': [stream.lon for stream in data_streams],
                      'sensor_name': [stream.sensor_name for stream in data_streams],
                      'loc': [stream.loc for stream in data_streams],
                      'channel': [stream.channel for stream in data_streams],
                      'data_type': [stream.data_type for stream in data_streams]
                      })
    
    return df
    








################################################################################
############################## Class Definitions ###############################
################################################################################


class DataStream:
    '''
    The DataStream class basically equates to a single CSV data file.
    
    Each purple air sensor should have four data streams (primary and secondary streams for two different channels)
    
    The DataStream is set up by parsing the file name to determine the following attributes:
            - loc: "inside", "outside", or "undefined" (all channel B streams are undefined)
            - sensor_name: name of the sensor that the stream belongs to
            - channel: "A" or "B"
            - data_type: 1 (primary dataset) or 2 (secondary) or 0 (unknown)
            - lat/lon: sensor coordinates
    
    
    '''
    
    def __init__(self,filepath):


        """
        Initialization of the DataStream.
        
        Inputs:
            - filepath (string): path to a CSV file
            
        The Purple Air CSV files have form:
        
        STATION NAME channel (loc) (lat lon) DataType 60_minute_average startdate enddate.csv 
        
        where startdate and enddate mark the time period for which the data was originally requested (so they should all be the same for this project)
        """
        
        self.filepath = filepath #full file path
        self.filename = filepath.split('./data/purple_air/')[1] # file name
        

        #### Find the sensor's location 
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
                

                
    
    
    def start_time(self):
        '''
        Determines when the DataStream's record begins.
        The study period spans from 05-01-2020 to 11-01-2020.
        Sensors that were up and running at the beginning of this period will return a start time of May 1.
        Inputs:
            - None
        Output:
            - start_time_dt (pandas timestamp): datetime corresponding to the first measurements in the DataStream. If the DataStream's time field is empty, function returns NaT (pandas Not-a-Time)
        '''
        
        #grabs the minimum time of the time field from the CSV
        start_time = pd.read_csv(self.filepath).created_at.min()
            
        return pd.to_datetime(start_time)
    
    
    
    
    
    def load(self):
        '''
        Reads in the DataStream's data from corresponding CSV file.
        Converts to an xarray dataset.
        Inputs:
            - None
        Outputs:
            - ds (xarray dataset)
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
        time = []
        for t in ds.time.values:
            if t.endswith('UTC'):
                time.append(np.datetime64(t[:-3].strip()))
            else:
                time.append(np.datetime64(t))
        ds['time'] = (('time'), np.array(time))

        # add some attributes with the DataStream info
        ds.attrs['sensor_name'] = self.sensor_name
        ds.attrs['channel'] = self.channel
        ds.attrs['loc'] = self.loc
        ds.attrs['data_type'] = self.data_type

        return ds
    
    
    
    
    
    
    
    
    
    
    
class Sensor:
    '''
    A Sensor instance describes one physical purple air sensor (and its unique location). 

    Each sensor has a name and lat/lon coordinates. The name of the sensor is not necessarily unique (since some names are just the neighborhood where the sensor is, and many neighborhoods have multiple sensors). But each sensor has a unique combination of name and lat/lon coordinates.

    Each Sensor instance is initialized with a list of its four correspondinig DataStream instances (see DataStreams.py).
    Each sensor has two channels (lasers) and two datasets (primary and secondary), for a total of 4 data files for each sensor
    '''
    
    def __init__(self, data_streams):
        
        #############
        ###### Check that "streams" contains no more than four DataStreams 
        if len(data_streams) != 4:
            raise ValueError("Input list must cannot contain more than 4 DataStreams")
        else:
            pass
        
        
        #############
        ###### Check that DataStreams all have the sensor name and coordinates
        
        name = data_streams[0].sensor_name
        lat = data_streams[0].lat
        lon = data_streams[0].lon
        
        # True if the DataStreams match identical
        name_check = all([stream.sensor_name == name for stream in data_streams ])
        lat_check = all([stream.lat == lat for stream in data_streams ])
        lon_check = all([stream.lon == lon for stream in data_streams ])
        
        # if all the sensor info matches -> assign to Sensor
        if name_check and lat_check and lon_check: 
            self.name = name
            self.lat = lat
            self.lon = lon
            
        else: # the DataStreams appear to be from different sensors
            raise ValueError("DataStreams must have identical sensor names")
        
        #############
        ###### Check that each DataStream has a valid channel
        
        channels = [stream.channel for stream in data_streams] # channels for each DataStream
        if any((channel != 'A' and channel != 'B') for channel in channels):
            raise ValueError("DataStreams much have valid channel IDs ('A' or 'B')")
           
        #############
        ###### Check that each DataStream has a valid data_type (1 or 2 for primary or secondary)
        ###### and that we have at least one primary DataStream
        
        data_types = [stream.data_type for stream in data_streams] # data types for each DataStream
        if any((dtype != 1 and dtype != 2) for dtype in data_types):
            raise ValueError("DataStreams much have valid data_types (1 for Primary, 2 for Secondary)")
            
        if all((dtype != 1) for dtype in data_types):
            raise ValueError("Input DataStreams must include at least one primary DataStream (data_type=1)")
        
        #############
        ###### Check that each DataStream has a unique combination of channel and data_type to avoid conflicts
        
        stream_info_tuples = [(channel, dtype) for channel, dtype in zip(channels, data_types)] # tuple for each DataStream of form (channel, data_type)
        if len(stream_info_tuples) != len(set(stream_info_tuples)):
            raise ValueError("DataStreams must all have unique combination of channel and data type.")
        else:
            pass
        
        #############
        ###### Get sensor location (outside, inside, or undefined)
        locs = set([stream.loc for stream in data_streams])
        
        if 'inside' in locs and 'outside' in locs:
            raise ValueError("Some DataStreams are inside and some are outside...")
        elif 'inside' in locs:
            self.loc = 'inside'
        elif 'outside' in locs:
            self.loc = 'outside'
        else:
            self.loc = 'undefined'
            
        #############
        ###### Validation finished
        
        self.datastreams = data_streams
        self.num_streams = len(data_streams)
        
        #loop through DataStreams and assign them according to channel and data type
        for stream in data_streams: 
            if stream.channel == 'A' and stream.data_type == 1:
                self.A1 = stream
            elif stream.channel == 'A' and stream.data_type == 2:
                self.A2 = stream
            elif stream.channel == 'B' and stream.data_type == 1:
                self.B1 = stream
            elif stream.channel == 'B' and stream.data_type == 2:
                self.B2 = stream
            else:
                pass
            
    
    
    def start_time(self):
        '''
        Determines the earliest date and time for which data is available from the sensor.
        This is equivalent to the earliest start time among the sensor's four DataStreams (data from all four streams need not be available at the start time)
        
        Inputs:
            -None
        Output:
            -start_time (pandas timestamp): the time of the first sensor measurement. If none of the Sensor's DataStreams have time information, NaT is returned (pandas Not-a-Time)
        '''
        start_times = pd.Series([stream.start_time() for stream in self.datastreams])
        
        start_time = start_times.min()

       
        return start_time
            
            
    
    
        
    def load(self):
        '''
        Loads and combines data from the sensor's DataStreams and returns as xarray Dataset.
        If the sensor is inside, we use the CF=1 data fields (CF is correction factor).
        If it's outside, we use the CF=ATM data fields.
        Data from channels A and B are added to the dataset (data from channel B have "b" at the end of the variable names)
        Dataset also includes latitude, longitude, pressure, temperature, relative humidity, and sensor uptime
        Inputs:
            - None
        Output: 
            - ds (xarray dataset): combined data from the sensor's DataStreams
        '''
        
        # load in the four datastreams from the sensor and get the time coordinate
        a1 = self.A1.load()
        a2 = self.A2.load()
        b1 = self.B1.load()
        b2 = self.B2.load()
        
        # get the time coordinate
        time = a1.time
        
        # start our new output dataset
        ds = xr.Dataset(coords={'time':time})
        
        # add in some station info
        ds.attrs = {'sensor_name': self.name,
                    'location': self.loc}
        
        # add our supplemental fields
        ds = ds.assign({'lat': self.lat,
                        'lon': self.lon,
                        'temp': a1.temp,
                        'rh': a1.rh,
                        'pressure': b1.pressure,
                        'uptime': a1.uptime})
        
        #############
        ###### Add in our PM data
        
        if self.loc == 'inside': # inside -> use CF=1 data
            ds = ds.assign({'pm1': a1.pm1_cf1,
                            'pm25': a1.pm25_cf1,
                            'pm10': a1.pm10_cf1,
                            'pm1b': b1.pm1_cf1, # channel B
                            'pm25b': b1.pm25_cf1,
                            'pm10b': b1.pm10_cf1})
            
        else: #outside or unknown -> use CF=ATM data
            ds = ds.assign({'pm1': a2.pm1_atm,
                            'pm25': a1.pm25_atm,
                            'pm10': a2.pm10_atm,
                            'pm1b': b2.pm1_atm, # channel B
                            'pm25b': b1.pm25_atm,
                            'pm10b': b2.pm10_atm})
        
        # add descriptive names and units
        fields = ['pm1','pm25','pm10','pm1b','pm25b','pm10b']
        particle_sizes = ['1.0','2.5','10']*2
        channels = 3*['A']+3*['B']
        
        for field, size, channel in zip(fields, particle_sizes, channels):
            ds[field].attrs = {'name': f'Concentration of particles smaller than {size} micron (Channel {channel})',
                               'units': 'ug/m3'}
           
        
        #############
        ###### Add in our number concentration data
        
        num_fields = ['n_pm03','n_pm05','n_pm1','n_pm25','n_pm5','n_pm10']
        particle_sizes = ['0.3','0.5','1.0','2.5','5.0','10.0']
        
        for field, size in zip(num_fields, particle_sizes): # loop through field names
            
            ds = ds.assign({field: a2[field],
                            field+'b': b2[field]})
            
            ds[field].attrs = {'name': f'Number concentration of particles smaller than {size} micron (Channel A)',
                               'units': 'dl-1'} #attributes for Channel A
            
            ds[field+'b'].attrs = {'name': f'Number concentration of particles smaller than {size} micron (Channel A)',
                               'units': 'dl-1'} #attributes for Channel B
            
        
        return ds