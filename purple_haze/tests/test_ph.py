#!/usr/bin/python
# -*- coding: utf-8 -*-
'''Set of tests for purple_haze modules

    Args:
        References data in data/
            seattle_ses_data/*
            purple_air/*
        and modules in purple_haze/
            air.py
            matcher.py

... Read more on the README:
https://github.com/UWSEDS/hw3-gretashum/blob/master/README.md

...to run me from main directory, type in terminal:
'python -m unittest purple_haze/tests/test_ph.py'

'''
import unittest
import numpy as np
import glob
import pandas as pd
import geopandas as gpd
from geopandas.tools import sjoin

from purple_haze import matcher
from purple_haze import air


class AirTests(unittest.TestCase):
    def test_edge_files_to_dataframe_0(self):
        '''
        Edge test for air module
        Function: files_to_dataframe

        Tests to see if __init__ catches error of
        entering files without being string

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''
        with self.assertRaises(TypeError):
            air.files_to_dataframe(glob(glob(5)))

    def test_edge_files_to_dataframe_1(self):
        '''
        Edge test for air module
        Function: files_to_dataframe

        Tests to see if __init__ catches error of
        entering files without being string

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''
        foo = 5
        with self.assertRaises(TypeError):
            air.files_to_dataframe(glob.glob(foo))

    def test_edge_files_to_dataframe_2(self):
        '''
        Edge test for air module
        Function: files_to_dataframe

        Checking to see if __init__ catches when
        file does not end in .csv

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''
        with self.assertRaises(ValueError):
            air.files_to_dataframe(
                'data/purple_air/10058 *ad (outside) * Primary 60_*11_01_2020'
            )

    def test_edge_files_to_dataframe_3(self):
        '''
        Edge test for air module
        Function: files_to_dataframe

        Checking to see if __init__ catches when
        filepath does not contain lat/lons

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''

        with self.assertRaises(ValueError):
            air.files_to_dataframe(
                'data/purple_air/10058 *(outside) Prim*.csv'
            )

    def test_oneshot_files_to_dataframe_0(self):
        '''
        One-Shot test for air module
        Function: files_to_dataframe

        Checking to see if __init__ can tell name even
        if location is unknown

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''

        sensor_data = air.files_to_dataframe(
            [
                'data/purple_air/Loc (tk) (47.0 -122.0) Primary 11_01_2020.csv'
            ]
        )
        print(sensor_data['sensor_name'])
        assert sensor_data['sensor_name'][0] == ('Loc').lower()

    def test_oneshot_files_to_dataframe_1(self):
        '''
        One-Shot test for air module
        Function: files_to_dataframe

        Checking to see if __init__ can tell name even
        if location is unknown

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''

        sensor_data = air.files_to_dataframe(
            [
                'data/purple_air/Loc (47.0 -122.0) Primary 11_01_2020.csv'
            ]
        )
        print(sensor_data['sensor_name'])
        assert sensor_data['sensor_name'][0] == ('Loc').lower()

    def test_oneshot_files_to_dataframe_2(self):
        '''
        One-Shot test for air module
        Function: files_to_dataframe

        Checking to see if __init__ fills in 'undefined'
        for sensor location if it is not a known location

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''

        sensor_data = air.files_to_dataframe(
            [
                'Loc (unknown_location) (47.0 -122.0) Primary 2020.csv'
            ]
        )
        assert sensor_data['loc'][0] == 'undefined'

    def test_edge_files_to_dataframe(self):
        '''
        Edge test for air module
        Function: files_to_dataframe

        raise error 'input must be string'

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''

        Location = 5
        with self.assertRaises(TypeError):
            air.files_to_dataframe(
                [Location]
            )

    def test_smoke_tract_files_to_sensors(self):
        '''
        Smoke test for air module
        Function: tract_files_to_sensors

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''
        sensor_data = air.files_to_dataframe(glob.glob('data/purple_air/*'))
        matched_ses_data = matcher.station_matcher(
            sensor_data, ses_directory='data/seattle_ses_data/ses_data.shp')

        sensors = matched_ses_data.apply(
            lambda df_row: air.get_tract_mean_aqi(df_row), axis=1)

        assert len(sensors) > 0

    def test_edge_tract_files_to_sensors_0(self):
        '''
        Edge test for air module
        Function: tract_files_to_sensors

        Checks to see if it catches that
        we've got fewer than 4 csvs
        Should raise:
        "Input list must contain four DataStreams"

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''
        sensor_data = air.files_to_dataframe(glob.glob(
            'data/purple_air/15th and Northgate B*'))
        matched_ses_data = matcher.station_matcher(
            sensor_data, ses_directory='data/seattle_ses_data/ses_data.shp')

        with self.assertRaises(ValueError):
            matched_ses_data.apply(
                lambda df_row: air.get_tract_mean_aqi(df_row), axis=1)

    def test_edge_tract_files_to_sensors_1(self):
        '''
        Edge test for air module
        Function: tract_files_to_sensors

        Checks to see if it catches that
        we've got duplicate inputs. Should raise
        "DataStreams must have all unique combinations"

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''
        sensor_data = air.files_to_dataframe(glob.glob(
            'data/purple_air/15th and Northgate B*'))
        sensor_data.append(air.files_to_dataframe(glob.glob(
            'data/purple_air/15th and Northgate B*')))
        matched_ses_data = matcher.station_matcher(
            sensor_data, ses_directory='data/seattle_ses_data/ses_data.shp')

        with self.assertRaises(ValueError):
            matched_ses_data.apply(
                lambda df_row: air.get_tract_mean_aqi(df_row), axis=1)

    def test_edge_tract_files_to_sensors_2(self):
        '''
        Edge test for air module
        Function: tract_files_to_sensors

        Checks to see if it catches that
        sensor streams must have same lat/lons.
        Should raise:
        "DataStreams must have matching \
        and lat/lon coordinates."

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''
        sensor_data = air.files_to_dataframe(glob.glob(
            'data/purple_air/15th and Northgate B*'))
        sensor_data['lat'][1] = 50
        matched_ses_data = matcher.station_matcher(
            sensor_data, ses_directory='data/seattle_ses_data/ses_data.shp')

        with self.assertRaises(ValueError):
            matched_ses_data.apply(
                lambda df_row: air.get_tract_mean_aqi(df_row), axis=1)

    def test_smoke_get_tract_mean_aqi(self):
        '''
        Smoke test for air module
        Function: get_tract_mean_aqi

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''
        sensor_data = air.files_to_dataframe(glob.glob('data/purple_air/*'))
        matched_ses_data = matcher.station_matcher(
            sensor_data, ses_directory='data/seattle_ses_data/ses_data.shp')

        matched_ses_data['mean_aqi'] = matched_ses_data.apply(
            lambda df_row: air.get_tract_mean_aqi(df_row), axis=1)
        assert len(matched_ses_data['mean_aqi']) > 0

    def test_oneshot_get_tract_mean_aqi(self):
        '''
        One shot test for air module
        Function: get_tract_mean_aqi

        Checking to see if air.get_tract_mean_aqi actually removes data
        from time period: 2020-09-08T00:00:00 to 2020-09-19T23:00:00,
        when include_smoke = False,

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''
        sensor_data = air.files_to_dataframe(glob.glob('data/purple_air/*'))
        matched_ses_data = matcher.station_matcher(
            sensor_data, ses_directory='data/seattle_ses_data/ses_data.shp')

        # making test input with no column called 'data_stream_file_names'
        non_smoke_matched_data = matched_ses_data.apply(
            lambda df_row: air.get_tract_mean_aqi(
                df_row, include_smoke=False), axis=1)
        print(non_smoke_matched_data.head)

    def test_edge_get_tract_mean_aqi(self):
        '''
        Edge test for air module
        Function: get_tract_mean_aqi

        Checking to see if air.get_tract_mean_aqi catches the error:
        when there is no column in df called 'data_stream_file_names',
        throw ValueError

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''
        sensor_data = air.files_to_dataframe(glob.glob('data/purple_air/*'))
        matched_ses_data = matcher.station_matcher(
            sensor_data, ses_directory='data/seattle_ses_data/ses_data.shp')

        # making test input with no column called 'data_stream_file_names'
        matched_ses_data_missing_names = matched_ses_data.drop(
            ['data_stream_file_names'], axis=1
        )
        with self.assertRaises(ValueError):
            matched_ses_data_missing_names.apply(
                lambda df_row: air.get_tract_mean_aqi(df_row), axis=1)

    def test_smoke_get_tract_exposure_0(self):
        '''
        Smoke test for air module
        Function: get_tract_exposure

        Smoke test to check that get_tract_exposure
        returns a returns some values (not nothing)

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''
        sensor_data = air.files_to_dataframe(glob.glob('data/purple_air/*'))
        matched_ses_data = matcher.station_matcher(
            sensor_data, ses_directory='data/seattle_ses_data/ses_data.shp')

        matched_ses_data['exp100'] = matched_ses_data.apply(
            lambda row: air.get_tract_exposure(row, 100), axis=1)
        assert len(matched_ses_data['exp100']) > 0

    def test_smoke_get_tract_exposure_1(self):
        '''
        Smoke test for air module
        Function: get_tract_exposure

        check to make sure it changes start/end times
        when include_smoke = False

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''

        sensor_data = air.files_to_dataframe(glob.glob('data/purple_air/*'))
        matched_ses_data = matcher.station_matcher(
            sensor_data, ses_directory='data/seattle_ses_data/ses_data.shp')

        matched_ses_data['exp100'] = matched_ses_data.apply(
            lambda row: air.get_tract_exposure(
                row, 100, include_smoke=False), axis=1
        )
        assert len(matched_ses_data['exp100']) > 0

    def test_edge_get_tract_exposure_0(self):
        '''
        Edge test for air module
        Function: get_tract_exposure

        AQI threshold given as string – should throw error because
        it should be given as an integer

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''
        sensor_data = air.files_to_dataframe(glob.glob('data/purple_air/*'))
        matched_ses_data = matcher.station_matcher(
            sensor_data, ses_directory='data/seattle_ses_data/ses_data.shp')

        with self.assertRaises(TypeError):
            matched_ses_data.apply(
                lambda row: air.get_tract_exposure(
                    row, aqi_threshold='100'), axis=1)

    def test_edge_get_tract_exposure_2(self):
        '''
        Edge test for air module
        Function: get_tract_exposure

        check to make sure it has column, 'data_stream_file_names'

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''
        sensor_data = air.files_to_dataframe(glob.glob('data/purple_air/*'))
        matched_ses_data = matcher.station_matcher(
            sensor_data, ses_directory='data/seattle_ses_data/ses_data.shp')

        matched_ses_data_missing_names = matched_ses_data.drop(
            ['data_stream_file_names'], axis=1)
        with self.assertRaises(ValueError):
            matched_ses_data_missing_names.apply(
                lambda df_row:
                air.get_tract_exposure(df_row, aqi_threshold=100), axis=1)

    def test_oneshot_aqi(self):
        '''
        One-shot test for air module
        Function: aqi

        Using the EPA calculator
        (https://cfpub.epa.gov/airnow/index.cfm?action=airnow.calculator)
        test if PM 2.5-to-AQI cacluator is accurate

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''
        pm25 = 45
        aqi = air.aqi(pm25)
        print(aqi)
        assert np.isclose(np.rint(aqi), 124)

    def test_edge_aqi(self):
        '''
        Edge test for air module
        Function: aqi

        Using the EPA calculator
        (https://cfpub.epa.gov/airnow/index.cfm?action=airnow.calculator)
        test if PM 2.5-to-AQI checks for error with negative AQI

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''
        pm25 = -45
        with self.assertRaises(ValueError):
            air.aqi(pm25)

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

        assert air.remove_utc(
            time_string_with
        ) == 'testerstring' and air.remove_utc(
            time_string_sans
        ) == 'testerstring_none'


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
        ses_file = 'data/seattle_ses_data/ses_data.shp'
        ses_data = gpd.read_file(ses_file)
        new_ses_data = ses_data.to_crs(epsg=4326)

        # convert input to GeoDataFrame using lat/lon
        data_stream_df = air.files_to_dataframe(
            glob.glob('data/purple_air/Green Lake SE*'))
        data_stream_gdf = gpd.GeoDataFrame(
            data_stream_df,
            geometry=gpd.points_from_xy(
                data_stream_df['lon'],
                data_stream_df['lat']),
            crs="EPSG:4326")

        # join the two dataframes
        # (must use "inner" to rerain sensor file names)
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
            lambda row: matcher.get_stream_names(
                aggregate, row['NAME10']), axis=1)

        our_names = new_ses_data['data_stream_file_names'].dropna()
        assert our_names.iloc[0].startswith('data/purple_air/Green Lake SE')

    def test_edge_get_stream_names(self):
        '''
        Edge test for matcher module
        Function: get_stream_names

        Some Purple Air data points are located outside Seattle.
        One example is:
        High Woodlands (47.735602 -122.182855)

        This test checks to see that that location
        does not appear in the output of matcher.get_stream_names

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''
        ses_file = 'data/seattle_ses_data/ses_data.shp'
        ses_data = gpd.read_file(ses_file)
        new_ses_data = ses_data.to_crs(epsg=4326)

        # convert input to GeoDataFrame using lat/lon
        data_stream_df = air.files_to_dataframe(glob.glob('data/purple_air/*'))
        data_stream_gdf = gpd.GeoDataFrame(
            data_stream_df,
            geometry=gpd.points_from_xy(
                data_stream_df['lon'],
                data_stream_df['lat']),
            crs="EPSG:4326")

        # join the two dataframes (must use "inner"
        # to rerain sensor file names)
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
            lambda row: matcher.get_stream_names(
                aggregate, row['NAME10']), axis=1)

        our_names = new_ses_data['data_stream_file_names'].dropna()
        assert our_names.iloc[0].startswith(
            'High Woodlands (outside)') is False

    def test_smoke_station_matcher(self):
        '''
        Smoke test for matcher module
        Function: station_matcher

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''
        sensor_data = air.files_to_dataframe(glob.glob('data/purple_air/*'))
        assert len(matcher.station_matcher(
            sensor_data, ses_directory='data/seattle_ses_data/ses_data.shp')
                  ) > 0

    def test_oneshot_station_matcher_0(self):
        '''
        One-shot test for matcher module
        Function: station_matcher

        We're testing one sensor to make sure
        PA sensor matches up with the correct census tract:
        Green Lake SE should be in Census Tract 46:

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''
        test_sensor_data = air.files_to_dataframe(
            glob.glob('data/purple_air/Green Lake SE*'))

        m = matcher.station_matcher(
            test_sensor_data,
            ses_directory='data/seattle_ses_data/ses_data.shp')
        non_zero = m[m['sensor_counts'] > 0]
#         print(non_zero['NAME10'].iloc[0])
        assert non_zero['NAME10'].iloc[0] == '46'

    def test_oneshot_station_matcher_1(self):
        '''
        One-shot test for matcher module
        Function: station_matcher

        We're testing one sensor to make sure
        it gets deleted because it's outside
        our Census Tract range.

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''
        test_sensor_data = air.files_to_dataframe(
            glob.glob('data/purple_air/CBF*'))

        m = matcher.station_matcher(
            test_sensor_data,
            ses_directory='data/seattle_ses_data/ses_data.shp')
        our_station = m[m['data_stream_file_names'] == 'data/purple_air/CBF*']
        print(our_station)
        assert len(our_station) == 0

    def test_oneshot_station_matcher_2(self):
        '''
        One-shot test for matcher module
        Function: station_matcher

        We're testing one sensor to make sure
        sensor matches up with the correct census tract:
        CBF should be in Census Tract 01:

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''
        test_sensor_data = air.files_to_dataframe(
            glob.glob('data/purple_air/CBF*'))

        m = matcher.station_matcher(
            test_sensor_data,
            ses_directory='data/seattle_ses_data/ses_data.shp')
        non_zero = m[m['sensor_counts'] > 0]
#         print(non_zero['NAME10'].iloc[0])
        assert non_zero['NAME10'].iloc[0] == '1'

    def test_edge_station_matcher(self):
        '''
        Edge test for matcher module
        Function: station_matcher

        Making a copy of Nickerson Marina csv,
        but renaming it to have lat-long in the water

        Returns:
            bool:
                True if successful, False otherwise.

        Test passes if True
        '''

        test_sensor_data = air.files_to_dataframe(
            glob.glob(
                'data/purple_air/Wallingford Seattle WA B (outside)*'
            ))
        with self.assertRaises(TypeError):
            matcher.station_matcher(
                test_sensor_data,
                ses_directory='data/seattle_ses_data/ses_data.shp')
