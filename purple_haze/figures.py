"""Figures module of the purple_haze package.

Functions:

sensor_count_plotting(ses_metric, renamed_ses_data): creates the scatter
plot plotting a mean SES metric vs the number of sensors in a census tract along
with a linear regression and r^2 value.

aqi_plotting(ses_metric, aqi_metric,renamed_ses_data): creates the scatter
plot plotting an ses_metric and aqi_metric for each census tract along with a linear
regression and r^2 value.

make_altair_chart(renamed_ses_data,SES_metric): creates an Altair chart
mapping the census tract data and coloring the tracts by an SES metric in a dropdown.

make_widgets(renamed_ses_data): creates two interactive widgets for both scatter plots.

display_app(renamed_ses_data): displays the application and creates the layout for
all three interactive plots, ready for use by Voila.

Purple Haze Project Group
CSE 583 Fall 2020
"""

import ipywidgets as widgets
from IPython.display import display
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as sc_stats
import altair as alt

def sensor_count_plotting(ses_metric, renamed_ses_data):
    """Creates a scatter plot with linear regression of an SES metric and sensor counts

    This function creates a scatter plot chart of an averaged SES metric value against
    the number of PurpleAir sensors within a census tract. Additionally, a linear
    regression is performed and plotted, with the r^2 value displayed on the figure.

    Args:
        - ses_metric (string): name of the SES metric to display on the y-axis
        - renamed_ses_data (GeoDataFrame): contains the census tract shapefile data
          along with additional aqi computations. Some column names were renamed
    """
    # group by the number of sensors in the tract
    grouped = renamed_ses_data.groupby('sensor_counts')

    # number of sensors in tract (x coordinate)
    num_sensors = np.array([name for name, group in grouped])

    # metric of interest (y coordinate)
    stat = np.array([group[ses_metric].mean() for name, group in grouped])

    # number of census tracts in the group
    tract_counts = np.array([group['OBJECTID'].count() for name, group in grouped])

    # regression
    slope, intercept, r_value, p_value, std_err = sc_stats.linregress(num_sensors, stat)

    # plot
    fig, ax = plt.subplots(figsize=(9, 5.4))
    ax.scatter(num_sensors, stat, s=tract_counts*10)
    ax.plot(num_sensors, num_sensors * slope + intercept, color='k')
    ax.text(x=0.7, y=0.9, s = 'r^2 = ' + str(round(r_value ** 2, 3)), fontsize=16,
             color='r', transform=ax.transAxes)
    plt.title(ses_metric + ' versus number of sensors by census tract', fontsize=18)
    plt.ylabel(ses_metric, fontsize=16)
    plt.xlabel('Sensors in census tract', fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.show()

def aqi_plotting(ses_metric, aqi_metric, renamed_ses_data):
    """Creates a scatter plot with linear regression of an SES metric and an AQI metric

    This function creates a scatter plot chart of an SES metric value for one census
    tract against an AQI metric. Additionally, a linear regression is performed and plotted,
    with the r^2 value displayed on the figure.
        Args:
        - ses_metric (string): name of the SES metric to display on the y-axis
        - aqi_metric (string): name of the AQI metric to display on the x-axis
        - renamed_ses_data (GeoDataFrame): contains the census tract shapefile data
          along with additional aqi computations. Some column names were renamed
    """

    # get AQI and SES data
    aqi = renamed_ses_data[aqi_metric]
    counts = renamed_ses_data[ses_metric]

    # regression (requires removal of NaN)
    mask = ~np.isnan(aqi) & ~np.isnan(counts)
    slope, intercept, r_value, p_value, std_err = sc_stats.linregress(aqi[mask], counts[mask])

    # plot
    fig, ax = plt.subplots(figsize=(9, 5.4))
    ax.scatter(aqi, counts)
    aqi_space = np.linspace(np.amin(aqi), np.amax(aqi))
    ax.plot(aqi_space, aqi_space * slope + intercept, color='k')
    ax.text(x=0.7, y=0.9, s = 'r^2 = ' + str(round(r_value ** 2, 3)), fontsize=16,
             color='r', transform=ax.transAxes)
    plt.title(ses_metric + ' versus ' + aqi_metric, fontsize=16)
    plt.ylabel(ses_metric, fontsize=16)
    plt.xlabel(aqi_metric, fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.show()

def make_altair_chart(renamed_ses_data, ses_metric):
    """Creates a map of Seattle divided by census tract and colored by an SES metric

    This function creates a map of Seattle by plotting shapefile data of each census tract
    using Altair to easily create the map and to allow for interactions.
        Args:
        - renamed_ses_data (GeoDataFrame): contains the census tract shapefile data
          along with additional aqi computations. Some column names were renamed
        - SES_metric (string): name of the SES metric to color the map with
        Returns:
        - chart (Altair chart object): the map as a chart object
    """

    # Convert geopandas data to geojson for use with Altair
    data  = alt.InlineData(values = renamed_ses_data.__geo_interface__,
                           format = alt.DataFormat(property='features',type='json'))

    # Choose the renderer to properly display in Jupyter Notebook, Jupyter Lab, and Voila
    alt.renderers.enable('kaggle')

    # Make the chart
    chart = alt.Chart(data).mark_geoshape(
        stroke='black', strokeWidth=0.5
    ).encode(
        color = alt.Color('properties.%s' % ses_metric,
                          type='quantitative', title='%s' % ses_metric),
        tooltip=[alt.Tooltip('properties.NAME10:N', title='Census Tract')]
    ).properties(
        width = 400,
        height = 750,
    )

    return chart

def make_widgets(renamed_ses_data):
    """Creates the scatter plots as interactive figures using ipywidgets

    This function creates the interactive widget instances for the scatter plots
    created by the sensor_count_plotting and aqi_plotting functions. The list of
    metrics for both SES and AQI data are found within this function.
    Args:
        - renamed_ses_data (GeoDataFrame): contains the census tract shapefile data
        along with additional aqi computations. Some column names were renamed
    Returns:
        - sensor (widget): An interactive dropdown widget changing the SES metric
        - aqi (widget): An interactive dropdown widget changing the AQI metric
    """

    # metric lists
    ses_metric_list = ['COMPOSITE', 'SOCIOECONO', 'HEALTH', 'POC_PRCT', 'NON_ENGLISH', 'LOW_INCOME']
    aqi_metric_list = ['mean_aqi','exp100', 'exp150', 'mean_aqi_ns', 'exp100_ns', 'exp150_ns']

    # interactive widgets
    sensor = widgets.interactive(sensor_count_plotting,
                 ses_metric=widgets.Dropdown(
                     options=ses_metric_list,
                     description='Socioeconomic metric'),
                 renamed_ses_data=widgets.fixed(renamed_ses_data))

    aqi = widgets.interactive(aqi_plotting,
                 ses_metric=widgets.Dropdown(
                     options=ses_metric_list,
                     description='Socioeconomic metric'),
                 aqi_metric = widgets.Dropdown(
                     options=aqi_metric_list,
                     description='Air Quality Metric'),
                 renamed_ses_data=widgets.fixed(renamed_ses_data))

    return sensor, aqi

def display_app(renamed_ses_data):
    """Creates the layout for and renders the interactive app.

    This function creates three output boxes for the three widgets and formats
    them such that the map is on the left and the two scatter plots are stacked
    vertically on the right.
    Args:
        - renamed_ses_data (GeoDataFrame): contains the census tract shapefile data
        along with additional aqi computations. Some column names were renamed
 """

    # create the boxes to hold the widgets and format them
    child1 = [widgets.Output()]
    child23= [widgets.Output() for _ in range(2)]
    right = widgets.VBox([child23[0],child23[1]])
    left = widgets.VBox(child1)
    box = widgets.HBox([left,right])
    box.layout.flex_flow='row'
    box.layout.justify_content='center'
    display(box)

    # create the scatter plot widgets
    (sensor,aqi) = make_widgets(renamed_ses_data)

    # display the widgets in their own boxes
    with child1[0]:
        # widgets.interactive does not work with Altair charts, but interact does
        widgets.interact(make_altair_chart,
            renamed_ses_data=widgets.fixed(renamed_ses_data),
            ses_metric = sorted(renamed_ses_data.keys()))

    with child23[0]:
        display(sensor)

    with child23[1]:
        display(aqi)
