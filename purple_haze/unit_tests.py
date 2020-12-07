#!/usr/bin/python
# -*- coding: utf-8 -*-
'''Set of tests for ../purple_haze/matcher.py module for various errors and accuracy

    Args:
        None

... Read more on the README:
https://github.com/UWSEDS/hw3-gretashum/blob/master/README.md

...to run me, type in terminal: 'python -m unittest purple_haze.unit_tests'

'''
import unittest
from unittest.mock import Mock
import numpy as np
import glob
import pandas as pd
import scipy.stats as sc_stats
import warnings
import geopandas as gpd
from geopandas.tools import sjoin

import matcher
import air

class AirTests(unittest.TestCase):
    def test_smoke_files_to_dataframe(self):
        '''
        Smoke test for air module
        Function: files_to_dataframe
                
        Returns:
            bool:
                True if successful, False otherwise.
            
        Test passes if True
        '''
        sensor_data = air.files_to_dataframe(glob.glob('../data/purple_air/*'))
        assert len(sensor_data) > 0

#     def test_smoke_tract_files_to_sensors(self):
#         '''
#         Smoke test for air module
#         Function: tract_files_to_sensors
                
#         Returns:
#             bool:
#                 True if successful, False otherwise.
            
#         Test passes if True
#         '''
#         sensor_data = air.files_to_dataframe(glob.glob('../data/purple_air/*'))
#         matched_ses_data = matcher.station_matcher(sensor_data)
        
#         sensors = matched_ses_data.apply(lambda df_row: air.get_tract_mean_aqi(df_row), axis=1)
        
#         assert len(sensors) > 0

#     def test_smoke_get_tract_mean_aqi(self):
#         '''
#         Smoke test for air module
#         Function: tract_files_to_sensors
                
#         Returns:
#             bool:
#                 True if successful, False otherwise.
            
#         Test passes if True
#         '''
#         sensor_data = air.files_to_dataframe(glob.glob('../data/purple_air/*'))
#         matched_ses_data = matcher.station_matcher(sensor_data)
        
#         matched_ses_data['mean_aqi'] = matched_ses_data.apply(lambda df_row: air.get_tract_mean_aqi(df_row), axis=1)
#         assert len(matched_ses_data['mean_aqi']) > 0
    
#     def test_smoke_get_tract_exposure_100(self):
#         '''
#         Smoke test for air module
#         Function: get_tract_exposure
                
#         Returns:
#             bool:
#                 True if successful, False otherwise.
            
#         Test passes if True
#         '''
#         sensor_data = air.files_to_dataframe(glob.glob('../data/purple_air/*'))
#         matched_ses_data = matcher.station_matcher(sensor_data)
        
#         matched_ses_data['exp100'] = matched_ses_data.apply(lambda row: air.get_tract_exposure(row, 100), axis=1)
#         assert len(matched_ses_data['exp100']) > 0
        
#     def test_oneshot_aqi(self):
#         '''
#         One-shot test for air module
#         Function: aqi
        
#         Using the EPA calculator (https://cfpub.epa.gov/airnow/index.cfm?action=airnow.calculator), test if PM 2.5-to-AQI cacluator is accurate
                
#         Returns:
#             bool:
#                 True if successful, False otherwise.
            
#         Test passes if True
#         '''
#         pm25 = 45
#         aqi = air.aqi(pm25)
#         print(aqi)
#         assert np.isclose(np.rint(aqi),124)
    
#     def test_edge_aqi(self):
#         '''
#         Edge test for air module
#         Function: aqi
        
#         Using the EPA calculator (https://cfpub.epa.gov/airnow/index.cfm?action=airnow.calculator), test if PM 2.5-to-AQI cacluator is accurate
                
#         Returns:
#             bool:
#                 True if successful, False otherwise.
            
#         Test passes if True
#         '''
#         pm25 = -45
#         with self.assertRaises(ValueError):
#             error = air.aqi(pm25)
#             print(error)
            
    def test_oneshot_remove_utc(self):
        '''
        One-shot test for air module
        Function: remove_utc
        
        Removing 'UTC' from time string:
                
        Returns:
            bool:
                True if successful, False otherwise.
            
        Test passes if True
        '''
        time_string_with = "testerstringUTC"
        time_string_sans = "testerstring_none"
        
        assert air.remove_utc(time_string_with) == 'testerstring' and air.remove_utc(time_string_sans) == 'testerstring_none'



class MatcherTests(unittest.TestCase):

    def test_one_shot_get_stream_names(self):
        '''
        One Shot test for matcher module
        Function: get_stream_names
                
        Returns:
            bool:
                True if successful, False otherwise.
            
        Test passes if True
        '''
        ses_file = '../data/seattle_ses_data/ses_data.shp'
        ses_data = gpd.read_file(ses_file)
        new_ses_data = ses_data.to_crs(epsg=4326)
        
        # convert input to GeoDataFrame using lat/lon
        data_stream_df = air.files_to_dataframe(glob.glob('../data/purple_air/Green Lake SE*'))
        data_stream_gdf = gpd.GeoDataFrame(
            data_stream_df,
            geometry=gpd.points_from_xy(
            data_stream_df['lon'],
            data_stream_df['lat']),
            crs="EPSG:4326")

        # join the two dataframes (must use "inner" to rerain sensor file names)
        combined = sjoin(new_ses_data,
                         data_stream_gdf,
                         how='inner',
                         op='intersects')

        # combine rows from same tract ('NAME10' is census tract name)
        grouped = combined.groupby('NAME10')

        # make new column containing CSV file names separated by commas
        aggregate = grouped.agg(
            all_names=pd.NamedAgg(column='file', aggfunc=','.join))

        # add CSV file names to SES dataset
        new_ses_data['data_stream_file_names'] = new_ses_data.apply(
            lambda row: matcher.get_stream_names(aggregate, row['NAME10']), axis=1)
        
        
        
        our_names = new_ses_data['data_stream_file_names'].dropna()
        assert our_names.iloc[0].startswith('../data/purple_air/Green Lake SE')

    def test_edge_get_stream_names(self):
        '''
        Edge test for matcher module
        Function: get_stream_names
        
        Some Purple Air data points are located outside Seattle. One example is:
        High Woodlands (outside) (47.735602 -122.182855) Primary 60_minute_average 05_01_2020 11_01_2020
        
        This test checks to see that that location does not appear in the output of matcher.get_stream_names
                
        Returns:
            bool:
                True if successful, False otherwise.
            
        Test passes if True
        '''
        ses_file = '../data/seattle_ses_data/ses_data.shp'
        ses_data = gpd.read_file(ses_file)
        new_ses_data = ses_data.to_crs(epsg=4326)
        
        # convert input to GeoDataFrame using lat/lon
        data_stream_df = air.files_to_dataframe(glob.glob('../data/purple_air/*'))
        data_stream_gdf = gpd.GeoDataFrame(
            data_stream_df,
            geometry=gpd.points_from_xy(
            data_stream_df['lon'],
            data_stream_df['lat']),
            crs="EPSG:4326")

        # join the two dataframes (must use "inner" to rerain sensor file names)
        combined = sjoin(new_ses_data,
                         data_stream_gdf,
                         how='inner',
                         op='intersects')

        # combine rows from same tract ('NAME10' is census tract name)
        grouped = combined.groupby('NAME10')

        # make new column containing CSV file names separated by commas
        aggregate = grouped.agg(
            all_names=pd.NamedAgg(column='file', aggfunc=','.join))

        # add CSV file names to SES dataset
        new_ses_data['data_stream_file_names'] = new_ses_data.apply(
            lambda row: matcher.get_stream_names(aggregate, row['NAME10']), axis=1)
        
        our_names = new_ses_data['data_stream_file_names'].dropna()
        assert our_names.iloc[0].startswith('High Woodlands (outside)') is False

    def test_smoke_station_matcher(self):
        '''
        Smoke test for matcher module
        Function: station_matcher
                
        Returns:
            bool:
                True if successful, False otherwise.
            
        Test passes if True
        '''
        sensor_data = air.files_to_dataframe(glob.glob('../data/purple_air/*'))
        assert len(matcher.station_matcher(sensor_data)) > 0

    def test_oneshot_station_matcher(self):
        '''
        One-shot test for matcher module
        Function: station_matcher
        
        We're testing one sensor to make sure it matches up with the correct census tract:
        Green Lake SE should be in Census Tract 46:
                
        Returns:
            bool:
                True if successful, False otherwise.
            
        Test passes if True
        '''
        test_sensor_data = air.files_to_dataframe(glob.glob('../data/purple_air/Green Lake SE*'))
        
        m = matcher.station_matcher(test_sensor_data)
        non_zero = m[m['sensor_counts']>0]
#         print(non_zero['NAME10'].iloc[0])
        assert non_zero['NAME10'].iloc[0] == '46'

    

if __name__ == '__main__':
    unittest.main()




