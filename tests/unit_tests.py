#!/usr/bin/python
# -*- coding: utf-8 -*-
'''Set of tests for ../purple_haze/matcher.py module for various errors and accuracy

    Args:
        None

... Read more on the README:
https://github.com/UWSEDS/hw3-gretashum/blob/master/README.md

...to run me, type in terminal: 'python -m unittest tests.unit_tests'

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


from purple_haze import matcher
from purple_haze import air

class AirTest(unittest.TestCase):
    def test_smoke(self):
        '''
        Smoke test to make sure output of air.py is not zero
                
        Returns:
            bool:
                True if successful, False otherwise.
            
        Test passes if True
        '''
        sensor_data = air.files_to_dataframe(glob.glob('../data/purple_air/*'))
        assert sensor_data is not None

class MatcherTest(unittest.TestCase):
    def test_smoke(self):
        '''
        Smoke test to make sure output of air.py is not zero
                
        Returns:
            bool:
                True if successful, False otherwise.
            
        Test passes if True
        '''
        sensor_data = air.files_to_dataframe(glob.glob('../data/purple_air/*'))
#         gpd.read_file = Mock()
#         ses_file = '../data/seattle_ses_data/ses_data.shp'
#         gpd.read_file.return_value = gpd.read_file(ses_file)
#         ses_file = gpd.read_file('../data/seattle_ses_data/ses_data.shp')
        assert gpd.read_file('data/seattle_ses_data/ses_data.shp') is not None
#         assert matcher.station_matcher(sensor_data) is not None

if __name__ == '__main__':
    unittest.main()