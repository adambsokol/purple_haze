'''
Module for the Sensor class.

A Sensor instance describes one purple air sensor (i.e., a location where somebody has put a Purple Air station). 

Each sensor has a name and lat/lon coordinates. The name of the sensor is not necessarily unique (since some names are just the neighborhood where the sensor is, and many neighborhoods have multiple sensors). But each sensor has a unique combination of name and lat/lon coordinates.

Each Sensor instance is initialized with a list of its four correspondinig DataStream instances (see DataStreams.py).
'''

import xarray as xr


class Sensor:
    '''
    This Sensor class represents one Purple Air sensor, which has unique lat/lon coordinates
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
        
        self.data_streams = data_streams
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
            
        
        
    def load(self):
        '''
        Loads data from the sensor's DataStreams and returns them as an Xarray dataset.
        If the sensor is inside, we use the CF=1 data fields (CF is correction factor).
        If it's outside, we use the CF=ATM data fields.
        Data from channels A and B are added to the dataset (data from channel B have "b" at the end of the variable names)
        Dataset also includes latitude, longitude, pressure, temperature, relative humidity, and sensor uptime
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