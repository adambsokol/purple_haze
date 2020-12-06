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

class AirTest(unittest.TestCase):
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

    def test_smoke_tract_files_to_sensors(self):
        '''
        Smoke test for air module
        Function: tract_files_to_sensors
                
        Returns:
            bool:
                True if successful, False otherwise.
            
        Test passes if True
        '''
        sensor_data = air.files_to_dataframe(glob.glob('../data/purple_air/*'))
        matched_ses_data = matcher.station_matcher(sensor_data)
        
        sensors = matched_ses_data.apply(lambda df_row: air.get_tract_mean_aqi(df_row), axis=1)
        
        assert len(sensors) > 0
        
    def test_smoke_tract_files_to_sensors(self):
        '''
        Smoke test for air module
        Function: tract_files_to_sensors
                
        Returns:
            bool:
                True if successful, False otherwise.
            
        Test passes if True
        '''
        sensor_data = air.files_to_dataframe(glob.glob('../data/purple_air/*'))
        matched_ses_data = matcher.station_matcher(sensor_data)
        
        sensors = matched_ses_data.apply(lambda df_row: air.get_tract_mean_aqi(df_row), axis=1)
        
        assert len(sensors) > 0

class MatcherTest(unittest.TestCase):
    def test_smoke(self):
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

    def test_oneshot_matcher_station_matcher(self):
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
    
    def test_oneshot_matcher_station_matcher(self):
        '''
        One-shot test for matcher module
        Function: get_stream_names
        
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




