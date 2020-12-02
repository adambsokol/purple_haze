"""Air module of the purple_haze package.

Functions:

files_to_dataframe(file_list): creates Dataframe of Purple Air CSV file
info.

tract_files_to_sensors(tract_files): converts CSV file names to Sensor
class instances.

get_tract_mean_aqi(df_row, include_smoke=True): calculates mean AQI
for a census tract.

get_tract_exposure(df_row, aqi_thresh, include_smoke=True): Calculates
exposure to some AQI threshold for a census tract.

aqi(pm25): calculates AQI based on PM2.5 data.


Classes:

DataStream: represents a single Purple Air CSV data file. Four
DataStreams are associated with a single Purple Air sensor.

Sensor: represents a single Purple Air sensor, which is associated
with four DataStreams.


Purple Haze Project Group
CSE 583 Fall 2020
"""

import re
import xarray as xr
import pandas as pd
import numpy as np

# Functions


def files_to_dataframe(file_list):
    """Makes dataframe of Purple Air CSV files

    This function creates a pandas dataframe with one row for each file
    in the input file_list and one column for each of the default
    attributes of the DataStream class.

    Args:
        - file_list (iterable of strings): names of files to include in
        dataframe
    Returns:
        - df (pandas DataFrame): contains one row for each CSV file in
        file_list and columns indicating the file name, latitude,
        longitude, sensor name, location, channel, and data type.
    """

    # convert file names to list of DataStream objects
    streams = [DataStream(file) for file in file_list]

    # make dataframe
    data_frame = pd.DataFrame({"file": file_list,
                               "lat": [st.lat for st in streams],
                               "lon": [st.lon for st in streams],
                               "sensor_name": [st.sensor_name
                                               for st in streams],
                               "loc": [st.loc for st in streams],
                               "channel": [st.channel for st in streams],
                               "data_type": [st.data_type for st in streams]
                               })
    return data_frame


def tract_files_to_sensors(tract_files):
    """Converts list of CSV file names to list of Sensor instances.

    Groups CSV files by sensor and initiates a Sensor class instance.

    Args:
        - tract_files (iterable of string): list of the paths of CSV
        files for Purple Air data located within a specific census
        tract.
    Returns:
        - sensors (list of Sensor instances): one Sensor for each
        Purple Air sensor in the census tract.
    """

    # Make DataStream instance from each CSV file
    streams = [DataStream(file) for file in tract_files]

    # use sensor name and lat to identify different sensors
    sens_info = set([(st.sensor_name, st.lat) for st in streams])

    # group DataStreams by sensor
    sens_stream_lists = []
    for (name, lat) in sens_info:

        # grabs list of DataStreams with matching info
        sens_streams = [st for st in streams
                        if st.sensor_name == name and st.lat == lat]

        sens_stream_lists.append(sens_streams)

    # initiate Sensor instance for each group of matching DataStreams
    sensors = [Sensor(sens_streams) for sens_streams in sens_stream_lists]

    return sensors


def get_tract_mean_aqi(df_row, include_smoke=True):
    """Gets mean outdoor AQI for a census tract

    Calculates the average AQI for the census tract using all
    available outdoor measurements. The mean AQI among different
    sensors is first calculated for each hour of the record, and
    the time-mean AQI is then found.

    Args:
        - df_row: row of a pandas dataframe that has column
        labeled "data_stream_file_names"
        - include_smoke (bool, default=True): if False, the smoky
        period between 2020-09-08T00:00 and 2020-09-19T23:00 is
        excluded from calculation.
    Returns:
        - mean_aqi (float): time- and sensor-averaged outdoor AQI
        for the census tract. NaN is returned
        if the tract has no outdoor sensors.
    """
    # If pd.isna(df_row['data_stream_file_names']):
    if df_row['sensor_counts'] == 0:
        return np.nan

    else:
        all_sensors = tract_files_to_sensors(
            df_row['data_stream_file_names'].split(','))

        outdoor_sensors = [sensor for sensor in all_sensors
                           if sensor.loc == 'outside']

        if len(outdoor_sensors) == 0:
            return np.nan

        else:
            dsets = [sensor.load() for sensor in outdoor_sensors]

            # pad each dataset with NaNs to fill the study time period
            times = np.arange(np.datetime64("2020-05-01T00:00:00"),
                              np.datetime64("2020-11-02T00:00:00"),
                              np.timedelta64(1, "h"))
            dsets = [ds.interp(time=times) for ds in dsets]

            # remove smoke period if desired
            if not include_smoke:
                start = np.datetime64("2020-09-08T00:00:00")
                end = np.datetime64("2020-09-19T23:00:00")
                dsets = [ds.where((ds.time < start) | (ds.time > end))
                         for ds in dsets]

            # find hourly mean AQI by averaging together sensors
            hourly_aqi = np.nanmean(np.stack([ds.aqi.values for ds in dsets]),
                                    axis=0)

            # return time-average AQI
            mean_aqi = np.nanmean(hourly_aqi)
            return mean_aqi


def get_tract_exposure(df_row, aqi_thresh, include_smoke=True):
    """Calculates exposure to AQI threshold for a census tract

    Uses all outdoor sensors in a census tract to calculate the average
    amount of time (in min/week) that tract AQI is above a provided
    threshold. Exposures are first calculated for each individual sensor, then
    averaged together.

    Args:
        - df_row: row of a pandas dataframe that has column
        labeled "data_stream_file_names"
        - aqi_threshold: threshold above whch exposure will be calculated
        - include_smoke (bool, default=True): if False, the smoky
        period between 2020-09-08T00:00 and 2020-09-19T23:00 is
        excluded from calculation.
    Returns:
        - tract_mean_exposure (float): tract-mean exposure to AQI above 100
        (in min/week)
    """

    # check that AQI threshold is positive integer
    if not isinstance(aqi_thresh, (int, float)):
        raise TypeError("AQI threshold must be numeric")

    if aqi_thresh <= 0:
        raise ValueError("AQI threshold must be greater than zero.")

    if df_row['sensor_counts'] == 0:
        return np.nan

    else:
        all_sensors = tract_files_to_sensors(
            df_row['data_stream_file_names'].split(','))

        outdoor_sensors = [sensor for sensor in all_sensors
                           if sensor.loc == 'outside']

        if len(outdoor_sensors) == 0:
            return np.nan

        else:
            dsets = [sensor.load() for sensor in outdoor_sensors]

            # remove smoke period if desired
            if not include_smoke:
                start = np.datetime64("2020-09-08T00:00:00")
                end = np.datetime64("2020-09-19T23:00:00")
                dsets = [ds.where((ds.time < start) | (ds.time > end))
                         for ds in dsets]

            exposures = [calculate_exposure(ds, aqi_thresh) for ds in dsets]
            tract_mean_exposure = np.nanmean(np.array(exposures))

            return tract_mean_exposure


def calculate_exposure(sensor_data, aqi_threshold):
    """Fraction of time that AQI exceeds threshold

    Args:
        - sensor_data: xarray datasets for a Purple Air sensor,
        such as that produced by Sensor.load()
        - aqi_threshold: threshold above which exposure will be
        calculated
    Returns:
        - exposure_fraction: fraction of hourly measurements with AQI
        exceeding aqi_threshold
    """

    num_measurements = (~np.isnan(sensor_data.aqi)).sum('time').values
    num_exceed = (sensor_data.aqi >= aqi_threshold).sum('time').values
    exposure_fraction = (60*num_exceed) / (num_measurements/24)
    return exposure_fraction


def aqi(pm25):
    """AQI Calculator

    Calculates AQI from PM2.5 using EPA formula and breakpoints from:
    https://www.airnow.gov/sites/default/files/2018-05/aqi-technical
    -assistance-document-may2016.pdf

    Args:
         - pm25 (int or float): PM2.5 in ug/m3
    """

    if pm25 < 0:
        raise ValueError("PM2.5 must be positive.")
    else:
        # round PM2.5 to nearest tenth for categorization
        pm25 = np.round(pm25, 1)

    green = {
        "aqi_low": 0,
        "aqi_hi": 50,
        "pm_low": 0.0,
        "pm_hi": 12.0
        }

    yellow = {
        "aqi_low": 51,
        "aqi_hi": 100,
        "pm_low": 12.1,
        "pm_hi": 35.4
        }

    orange = {
        "aqi_low": 101,
        "aqi_hi": 150,
        "pm_low": 35.5,
        "pm_hi": 55.4
        }

    red = {
        "aqi_low": 151,
        "aqi_hi": 200,
        "pm_low": 55.5,
        "pm_hi": 150.4
        }

    purple = {
        "aqi_low": 201,
        "aqi_hi": 300,
        "pm_low": 150.5,
        "pm_hi": 250.4
        }

    maroon = {
        "aqi_low": 301,
        "aqi_hi": 500,
        "pm_low": 250.5,
        "pm_hi": 500.4
        }

    colors = [green, yellow, orange, red, purple, maroon]
    categorized = False

    # Assign measurement to AQI category.
    for color in colors:
        if pm25 >= color["pm_low"] and pm25 <= color["pm_hi"]:
            cat = color
            categorized = True
            break
        else:
            pass

    # Put in highest category if still not assigned.
    if not categorized:
        cat = colors[-1]

    # EPA formula for AQI.
    aqi_num = (cat["aqi_hi"] - cat["aqi_low"]) / \
              (cat["pm_hi"] - cat["pm_low"]) * \
              (pm25 - cat["pm_low"]) + cat["aqi_low"]

    return aqi_num


# Class Definitions

class DataStream:
    """Class for single Purple Air dataset corresponding to one CSV file

    The DataStream class basically equates to a single CSV data file.
    Each purple air sensor should have four DataStreams: primary and
    secondary streams for two different channels.

    Parameters:
        - loc (string): location of the air quality monitor ("inside",
        "outside", or "undefined").

        - sensor_name (string): name of the sensor that the DataStream
        belongs to.

        - channel (string): "A" or "B". Air quality is measured on two
        channels (corresponding to laser wavelengths)

        - data_type (int): 1 (primary), 2 (secondary), or 0 (unknown)

        - lat (float): latitude of the sensor that the DataStream
        belongs to

        - lon (float): longitude of the sensor that the DataStream
        belongs to
    """

    def __init__(self, filepath):

        """Initialization of the DataStream class from a CSV file path.

        Parses the input file name to determine several details about
        the DataStream (loc, sensor_name, chennel, data_type, lat/lon)

        The Purple Air CSV files have form:
        STATION NAME channel (loc) (lat lon) DataType ...
        60_minute_average startdate enddate.csv

        where startdate and enddate mark the time period for which the
        data was originally requested (should all be the same for this
        project)

        Args:
            - filepath (string): path to a CSV file downloaded from
            Purple Air
        """

        # File info.
        self.filepath = filepath
        self.filename = filepath.split("./data/purple_air/")[1]

        # Find location.
        loc_options = ["(inside)", "(outside)", "(undefined)"]
        found_loc = False

        for loc_option in loc_options:

            if loc_option in self.filename.lower():

                # Found location.
                self.loc = loc_option[1:-1]  # Removes paretheses.

                # Retrieve sensor name and other parameters
                name, data_info = self.filename.split(loc_option)
                self.sensor_name = name.strip()

                # Determine channel (channel B has "B" in sensor name)
                if self.sensor_name.endswith(" B"):
                    self.channel = "B"

                    # Remove channel label from the sensor name.
                    self.sensor_name = self.sensor_name[:-1].strip().lower()

                else:
                    self.channel = "A"
                    self.sensor_name = self.sensor_name.lower()

                # Determine data_type.
                if "Primary" in data_info:
                    self.data_type = 1

                elif "Secondary" in data_info:
                    self.data_type = 2

                else:
                    # Unknown.
                    self.data_type = 0

                # Determine lat/lon coordinates.
                latlon_regex_pattern = r"\([0-9]+.[0-9]+ [-]+[0-9]+.[0-9]+\)"
                search_result = re.search(latlon_regex_pattern, data_info)

                if search_result:
                    # Coordinates were found.
                    crd_string = search_result.group()[1:-1]  # Removes parens.
                    lat_string, lon_string = crd_string.split()
                    self.lat = float(lat_string)
                    self.lon = float(lon_string)

                else:
                    # No coordinates found.
                    raise ValueError("Could not determine sensor \
                                      coordinates from the file name.")

                found_loc = True

                break

        if not found_loc:
            raise ValueError("Could not determine sensor location \
                            (inside/outside/undefined) from file name.")

    def start_time(self):
        """Finds beginning of the DataStream's record.

        The start time is the earliest measurement contained in the
        DataStream. For sensors that predate the beginning ot the
        study period (May 1, 2020), the DataStream start time is the
        beginning of the study period.

        Returns:
            - start_time (numpy datetime64): the first measurements in
            the DataStream.
        """

        # grabs the minimum time of the time field from the CSV
        start_time = pd.read_csv(self.filepath).created_at.min()

        # remove time zone if it"s there
        if start_time.endswith("UTC"):
            start_time = start_time[:-3].strip()
        else:
            pass

        return np.datetime64(start_time)

    def load(self):
        """Loads measurement data from the DataStream CSV file.

        Some variables are given friendlier names. Time data is
        converted to numpy datetime64 format.

        Returns:
            - ds (xarray dataset): data from CSV file
        """

        # Read into an xarray dataset via a dataframe
        dframe = pd.read_csv(self.filepath, index_col="created_at")
        dset = xr.Dataset.from_dataframe(dframe)

        # Drop unneeded fields
        drops = ["Unnamed: 9", "RSSI_dbm", "IAQ", "ADC"]
        drops = drops + [k for k in dset.keys() if k.startswith(">")]

        for var in drops:
            if var in dset:
                dset = dset.drop(var)
            else:
                pass

        # Make some friendlier names for the data fields
        rename = {
            "created_at": "time",
            "Pressure_hpa": "pressure",
            "PM1.0_CF1_ug/m3": "pm1_cf1",
            "PM2.5_CF1_ug/m3": "pm25_cf1",
            "PM10.0_CF1_ug/m3": "pm10_cf1",
            "PM2.5_ATM_ug/m3": "pm25_atm",
            "PM1.0_ATM_ug/m3": "pm1_atm",
            "PM10_ATM_ug/m3": "pm10_atm",
            "UptimeMinutes": "uptime",
            "Temperature_F": "temp",
            "Humidity_%": "rh"
            }

        # Loop through and rename the variables
        for old_name, new_name in rename.items():
            if old_name in dset:
                dset = dset.rename({old_name: new_name})
            else:
                pass

        # Assign units

        # Fields with units ug/m3
        ug_m3 = [
            "pm1",
            "pm25",
            "pm10",
            "pm25_atm",
            "pm1_atm",
            "pm10_atm"
            ]

        for field in dset.keys():
            if field in ug_m3:
                dset[field].attrs["units"] = "ug/m3"
            elif field == "temp":
                dset[field].attrs["units"] = "F"
            elif field == "pressure":
                dset[field].attrs["units"] = "hpa"
            elif field == "rh":
                dset[field].attrs["units"] = "%"
            else:
                pass

        # Convert time to numpy datetime64
        time = []
        for times in dset.time.values:
            if times.endswith("UTC"):
                time.append(np.datetime64(times[:-3].strip()))
            else:
                time.append(np.datetime64(times))
        dset["time"] = (("time"), np.array(time))

        # Add some attributes with the DataStream info
        dset.attrs["sensor_name"] = self.sensor_name
        dset.attrs["channel"] = self.channel
        dset.attrs["loc"] = self.loc
        dset.attrs["data_type"] = self.data_type

        return dset


class Sensor:
    """Represents a single Purple Air air quality monitor.

    A Sensor instance describes one Purple Air air quality sensor with a
    unique location. Each sensor has a name and lat/lon coordinates, and
    should have four associated DataStreams. The sensor name is not
    necessarily unique (since some names are just the neighborhood where
    the sensor is, and some neighborhoods have multiple sensors). But
    each combinatin of sensor name and coordinates (either lat or lon,
    or both) is unique.

    Each sensor is associated with four CSV data files (and therefore
    four DataStream instances): two channels (laser wavelengths) and two
    dataset types (primary and secondary).

    Parameters:
        - loc (string): "inside", "outside", or "undefined".

        - name (string): name of the sensor.

        - lat (float): latitude

        - lon (float): longitude

        - datastreams (list of DataStream instances): DataStreams
        associated with the sensor

        - num_streams (int): number of DataStreams associated with the
        sensor.

        - A1 (DataStream instance): parimary channel A DataStream.

        - A2 (DataStream instance): secondary channel A DataStream.

        - B1 (DataStream instance): parimary channel B DataStream.

        - B2 (DataStream instance): secondary channel B DataStream.
    """

    def __init__(self, data_streams):
        """Initialization of the Sensor class.

        Args:
            - data_streams (list of DataStream instances): list of the
            four DataStreams associated with the sensor.
        """

        # Check for exactly four DataStreams.
        if len(data_streams) != 4:
            raise ValueError("Input list must contain four DataStreams")
        else:
            pass

        # DataStreams must have same sensor_name and coordinates.
        name0 = data_streams[0].sensor_name
        name_check = all([stream.sensor_name == name0 for
                          stream in data_streams])

        lat0 = data_streams[0].lat
        lat_check = all([stream.lat == lat0 for stream in data_streams])

        lon0 = data_streams[0].lon
        lon_check = all([stream.lon == lon0 for stream in data_streams])

        # If DataStream info all matches -> assign to Sensor
        if name_check and lat_check and lon_check:
            pass
        else:
            # DataStreams do not all belong to the same sensor.
            raise ValueError("DataStreams must have identical sensor names")

        # Check for valid DataStream channels
        chans = [stream.channel for stream in data_streams]

        if any((channel != "A" and channel != "B") for channel in chans):
            raise ValueError("DataStreams must have valid channel IDs \
                ('A' or 'B')")

        # Check that data_types are valid, with at least one primary stream.
        dtypes = [stream.data_type for stream in data_streams]

        if any((dtype != 1 and dtype != 2) for dtype in dtypes):
            raise ValueError("DataStreams must have known data_types \
                (1 for Primary, 2 for Secondary)")

        if all((dtype != 1) for dtype in dtypes):
            raise ValueError("Input DataStreams must include at least one \
                primary DataStream (data_type=1)")

        # Check that Streams each have unique combo of channel and data_type.
        stream_info_tuples = [(chan, dt) for chan, dt in zip(chans, dtypes)]

        if len(stream_info_tuples) != len(set(stream_info_tuples)):
            raise ValueError("DataStreams must all have unique combination \
                of channel and data type.")
        else:
            pass

        # Check that DataStream locs do not conflict.
        locs = set([stream.loc for stream in data_streams])

        if "inside" in locs and "outside" in locs:
            raise ValueError("DataStreams have conflicting locations.")
        else:
            pass

        # Validation of inputs is now complete.

        # Assign sensor parameters.
        self.name = name0
        self.lat = lat0
        self.lon = lon0
        self.datastreams = data_streams
        self.num_streams = len(data_streams)

        # Get sensor location.
        if "inside" in locs:
            self.loc = "inside"

        elif "outside" in locs:
            self.loc = "outside"

        else:
            self.loc = "undefined"

        # Assign DataStreams according to channel and data_type.
        for stream in data_streams:
            if stream.channel == "A" and stream.data_type == 1:
                self.str_a1 = stream
            elif stream.channel == "A" and stream.data_type == 2:
                self.str_a2 = stream
            elif stream.channel == "B" and stream.data_type == 1:
                self.str_b1 = stream
            elif stream.channel == "B" and stream.data_type == 2:
                self.str_b2 = stream
            else:
                pass

    def start_time(self):
        """ Finds beginning of data record.

        Similar to DataStream.start_time() but for the Sensor class. If
        the Sensor's DataStreams have different start times, the
        earliest is returned.

        Returns:
            start_time (numpy datetime64): beginning of data reord.
        """

        # Get start time for each DataStream
        start_times = pd.Series([s.start_time() for s in self.datastreams])
        start_time = start_times.min()
        return start_time

    def load(self):
        """Loads and combines data from the sensor's DataStreams.

        Returns:
            - ds (xarray dataset): combined data for the sensor. If the
            sensor is inside, the Correction Factor = 1 data is
            included. If outside, Correction Factor = ATM data is used.
            Data from channel B have "b" at the end of the variable
            name. Dataset also includes lat, lon, pressure, temperature,
            relative humidity, and sensor uptime.
        """

        # Load in the four DataStreams.
        # Loading them into an array to minimize local variables
        # and make pep8 happy.
        dstreams = np.array([self.str_a1.load(),
                            self.str_a2.load(),
                            self.str_b1.load(),
                            self.str_b2.load()])

        # Initialize output dataset with the time coordinate.
        dset = xr.Dataset(coords={"time": dstreams[0].time})

        # Add in sensor info to dataset attributes.
        dset.attrs = {"sensor_name": self.name,
                      "location": self.loc}

        # Add supplmental fields.
        supp_fields = {
            "lat": self.lat,
            "lon": self.lon,
            "temp": dstreams[0].temp,
            "rh": dstreams[0].rh,
            "pressure": dstreams[2].pressure,
            "uptime": dstreams[0].uptime
            }
        dset = dset.assign(supp_fields)

        # Add proper particulate matter data depending on location.
        if self.loc == "inside":
            # Use CF=1 data.
            data_dict = {
                "pm1": dstreams[0].pm1_cf1,
                "pm25": dstreams[0].pm25_cf1,
                "pm10": dstreams[0].pm10_cf1,
                "pm1b": dstreams[2].pm1_cf1,
                "pm25b": dstreams[2].pm25_cf1,
                "pm10b": dstreams[2].pm10_cf1
                }
        else:
            # Use CF=ATM data.
            data_dict = {
                "pm1": dstreams[1].pm1_atm,
                "pm25": dstreams[0].pm25_atm,
                "pm10": dstreams[1].pm10_atm,
                "pm1b": dstreams[3].pm1_atm,
                "pm25b": dstreams[2].pm25_atm,
                "pm10b": dstreams[3].pm10_atm
                }

        dset = dset.assign(data_dict)

        # Calculate AQI.
        dset["aqi"] = (("time"), np.vectorize(aqi)(dset.pm25))

        # Invalidate data if more than 10% of AQI measurements are zero.
        num_zero = (dset.aqi == 0).sum("time").values
        num_numeric = (~np.isnan(dset.aqi)).sum("time").values
        if num_zero / num_numeric > 0.1:
            dset["aqi"] = (("time"), np.full(dset.dims["time"], np.nan))

        # Add descriptive names and units.
        fields = ["pm1", "pm25", "pm10", "pm1b", "pm25b", "pm10b"]
        particle_sizes = ["1.0", "2.5", "10"] * 2
        channels = 3 * ["A"] + 3 * ["B"]

        for field, size, chan in zip(fields, particle_sizes, channels):
            dset[field].attrs = {
                "name": f"Conc of particles smaller than {size} micron \
                    (Channel {chan})",
                "units": "ug/m3"
                }

        return dset
