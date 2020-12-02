"""Module for matching Purple Air sensors and census tracts

Functions:

station_matcher(data_stream_df): joins Purple Air CSV file dataframe
with census tract socioeconomic data

get_stream_names(data_array, name10): helper functions that gets the
DataStream file names for each census tract.

count_csv_files(files_string): determines the number of of DataStream
CSV files within each census tract.

Purple Haze Project Groups
CSE 583 Fall 2020

import air as air
import matcher as match
data_stream_info = air.files_to_dataframe(glob.glob('../data/purple_air/*'))
matched_ses_data = match.station_matcher(data_stream_info)
"""

import geopandas as gpd
from geopandas.tools import sjoin
import numpy as np
import pandas as pd


def station_matcher(data_stream_df):
    """ Matches Purple Air data with census tracts

    This function reads in the census-tract-level socioenconomic
    dataset and joins it with the input Purple Air DataStreams.

    Args:

    data_stream_df (pandas dataframe): dataframe containing one row for
    each DataStream CSV file. Columns must include "lat" and "lon". A
    suitable dataframe can be generated by air.files_to_dataframe().

    Returns:

    new_ses_data (pandas dataframe): tract-level socioeconomic dataset
    with an added column containing the paths to the CSV files for
    DataStreams contained within each tract. The CSV file paths are
    provided as a single string, with paths separated by commas.
    """
    # load socioeconomic dataset
    ses_file = '../data/seattle_ses_data/ses_data.shp'
    ses_data = gpd.read_file(ses_file)
    new_ses_data = ses_data.to_crs(epsg=4326)
    # convert input to GeoDataFrame using lat/lon
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
        lambda row: get_stream_names(aggregate, row['NAME10']), axis=1)
    # number of datastream CSV files for each tract
    new_ses_data['datastream_counts'] = new_ses_data.apply(
        lambda row: count_csv_files(row['data_stream_file_names']),
        axis=1)
    # number of Sensors in each tract (number of CSV files divided by 4)
    new_ses_data['sensor_counts'] = new_ses_data['datastream_counts'] / 4
    return new_ses_data


def get_stream_names(data_array, name10):
    """Retrieves data stream files for census tract

    Helper function that grabs the data stream file names in each
    census tract from the joined dataframe to append to the SES data.
    If there are no data streams in a census tract it returns NaN.

    Args:
        data_array (Pandas or GeoPandas dataframe): the combined array
        containing identifiers of the census tract (NAME10) and a column
        of comma separated values of each datastream in that census tract.
        name10 (string): a unique string that identifies each census tract

    Returns:
        names (string): the comma separated datastreams for the census tract
        given in the Args. Returns nan if there are no datastreams.
    """
    try:
        names = data_array['all_names'][name10]
    except (NameError, KeyError):
        names = np.nan
    return names


def count_csv_files(files_string):
    """Count number of DataStream CSV files in census tract

    Parses a string of CSV file paths to determine how many
    individual files there are.

    Args:
        files_string (string): single string of file paths separated by
        commas

    Returns:
        counts (int): number of CSV files
    """
    new_files_string = str(files_string)
    if new_files_string == 'nan':
        return 0
    return new_files_string.count(",") + 1
