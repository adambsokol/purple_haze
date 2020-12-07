"""Figures module of the purple_haze package.

Functions:

sensor_count_plotting(ses_metric, ses_data): makes a
scatterplot of census tract socioeconomic metrics against the number of
Purple Air sensors in each tract.

aqi_plotting(ses_metric, aqi_metric, ses_data): makes a
scatterplot of a census tract socioeconomic and air quality metrics.

make_altair_chart(ses_data, SES_metric): creates an Altair
chart mapping the census tract data and coloring the tracts by a
selected socioeconomic metric.

make_widgets(ses_data): creates two interactive widgets for
both scatter plots.

display_app(ses_data): displays application and creates the
layout for all three interactive plots, ready for use by Voila.

Purple Haze Project Group
CSE 583 Fall 2020
"""

import ipywidgets as widgets
from IPython.display import display
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as sc_stats
import altair as alt
import matcher as match


def sensor_count_plotting(ses_metric, ses_data):
    """Scatter plot of SES metric and sensor counts

    This function groups the census tracts by the number of Purple Air
    sensors in each tract, then computes and plots the mean
    socioeconomic metric among the tracts in each group. The generated
    plot has the number of sensors on the x-axis and the socioeconomic
    metric on the y-axis. A linear regression line is also plotted and
    the correlation coefficient displayed.

    Args:
        - ses_metric (string): socioeconomic metric (x-coordinate)
        - ses_data (GeoDataFrame): contains census tract shapefile data
          along with additional Purple Air sensor information.
    """
    # Group by census tract sensor count.
    grouped = ses_data.groupby("sensor_counts")

    # Number of sensors in tract (x-coordinate).
    num_sensors = np.array([name for name, group in grouped])

    # Get mean of socioeconomic metric for each sensor count group.
    stat = np.array([group[ses_metric].mean() for name, group in grouped])

    # Number of census tracts in each sensor count group.
    tract_counts = np.array(
        [group["OBJECTID"].count() for name, group in grouped])

    # Linear regression.
    m, b, corr_coef, p, std_err = sc_stats.linregress(num_sensors, stat)

    # Make the plot.
    plt.figure(figsize=(9, 5.4))
    plt.scatter(num_sensors, stat, s=tract_counts*10)
    plt.plot(num_sensors, num_sensors * m + b, color="k")
    plt.text(
        x=0.7, y=0.9, s=r"r$^2$ = {:.3f}".format(round(corr_coef ** 2, 3)),
        fontsize=16, color="r", transform=plt.gca().transAxes)
    plt.title(
        f"{ses_metric} vs. number of sensors in census tract",
        fontsize=18)
    plt.ylabel(ses_metric, fontsize=16)
    plt.xlabel("Sensors in census tract", fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.show()

    return


def aqi_plotting(ses_metric, aqi_metric, ses_data):
    """Scatterplot of socioeconomic vs air quality metrics

    This function creates a scatter plot chart of the selected air
    quality (x-axis) and socioeconomic (y-axis) metrics. Each point on
    the plot represents one census tract. A linear regression line is
    also plotted and the correlation coefficient displayed.

    Args:
        - ses_metric (string): socioeconomic metric (y-axis)
        - aqi_metric (string): air quality metric (x-axis)
        - ses_data (GeoDataFrame): contains census tract shapefile data
          along with additional Purple Air sensor information.
    """

    # Get the selected air quality and SES data.
    aqi = ses_data[aqi_metric]
    counts = ses_data[ses_metric]

    # Remove NaNs and compute regression.
    mask = ~np.isnan(aqi) & ~np.isnan(counts)
    m, b, corr_coef, p, std_err = sc_stats.linregress(aqi[mask], counts[mask])

    # Make the figure.
    plt.figure(figsize=(9, 5.4))
    plt.scatter(aqi, counts)
    aqi_pts = np.linspace(np.amin(aqi), np.amax(aqi))
    plt.plot(aqi_pts, aqi_pts * m + b, color="k")
    plt.text(
        x=0.7, y=0.9, s=r"r$^2$ = {:.3f}".format(round(corr_coef ** 2, 3)),
        fontsize=16, color="r", transform=plt.gca().transAxes)
    plt.title(f"{ses_metric} vs. {aqi_metric}", fontsize=16)
    plt.ylabel(ses_metric, fontsize=16)
    plt.xlabel(aqi_metric, fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.show()

    return


def make_altair_chart(ses_data, ses_metric):
    """Creates a tract-level map of the selected tract-level metric.

    This function creates a map of Seattle showing the selected
    socioeconomic or air quality metric at the census tract level. The
    map is created using Altair with interactions enabled.

    Args:
        - ses_data (GeoDataFrame): contains census tract shapefile data
          along with additional Purple Air sensor information.
        - ses_metric (string): socioeconomic metric to be plotted.
    Returns:
        - chart (Altair chart object): the map as a chart object
    """

    # Convert geopandas data to geojson for use with Altair.
    data = alt.InlineData(
        values=ses_data.__geo_interface__,
        format=alt.DataFormat(property="features", type="json"))

    # Choose renderer for proper display with Jupyter and Voila.
    alt.renderers.enable("kaggle")

    # Make the chart.
    chart = alt.Chart(data).mark_geoshape(
        stroke="black",
        strokeWidth=0.5
    ).encode(
        color=alt.Color(
            f"properties.{ses_metric}",
            type="quantitative",
            title=ses_metric),
        tooltip=[alt.Tooltip("properties.NAME10:N", title="Census Tract")]
    ).properties(
        width=400,
        height=750,
    )

    return chart


def make_widgets(ses_data):
    """Creates interactive scatter plots using ipywidgets.

    This function creates interactive widget instances for the scatter
    plots created by sensor_count_plotting and aqi_plotting. The list
    of socioeconomic and air quality metrics appearing in the dropdown
    menus are established here.

    Args:
        - ses_data (GeoDataFrame): contains census tract shapefile data
          along with additional Purple Air sensor information.
    Returns:
        - sensor (widget): interactive dropdown widget for selecting
          socioeconomic metrics.
        - aqi (widget): interactive dropdown widget for selecting air
          quality metrics.
    """

    # Retrieve list of socioeconomic matrics.
    ses_metrics = match.ses_name_mappings.values()

    # Remove quintile metrics since they are encoded as strings.
    ses_metric_list = [met for met in ses_metrics if "quintile" not in met]

    # List of air quality metric options.
    aqi_metric_list = [
        "mean_aqi",
        "exposure_aqi100",
        "exposure_aqi150",
        "mean_aqi_no_smoke",
        "exposure_aqi100_no_smoke",
        "exposure_aqi150_no_smoke"
    ]

    # Build interactive widgets.
    sensor_widget = widgets.interactive(
        sensor_count_plotting,
        ses_metric=widgets.Dropdown(
            options=ses_metric_list,
            description="Socioeconomic metric"),
        ses_data=widgets.fixed(ses_data))

    aqi_widget = widgets.interactive(
        aqi_plotting,
        ses_metric=widgets.Dropdown(
            options=ses_metric_list,
            description="Socioeconomic metric"),
        aqi_metric=widgets.Dropdown(
            options=aqi_metric_list,
            description="Air Quality Metric"),
        ses_data=widgets.fixed(ses_data))

    return sensor_widget, aqi_widget


def display_app(ses_data):
    """Creates the layout for and renders the interactive app.

    This function creates three output boxes for the three app widgets.
    The map widget is on the left, and the two scatterplot widgets are
    stacked vertically on the right.

    Args:
        - ses_data (GeoDataFrame): contains census tract shapefile data
          along with additional Purple Air sensor information.
    """

    # Create and format boxes to hold widgets.
    child1 = [widgets.Output()]
    child23 = [widgets.Output() for _ in range(2)]
    right = widgets.VBox([child23[0], child23[1]])
    left = widgets.VBox(child1)
    box = widgets.HBox([left, right])
    box.layout.flex_flow = "row"
    box.layout.justify_content = "center"
    display(box)

    # Create the scatter plot widgets.
    (sensor_widget, aqi_widget) = make_widgets(ses_data)

    # Display the widgets in their respective boxes.
    with child1[0]:
        # Altair chart requires widgets.interact (not widgets.interactive).
        widgets.interact(
            make_altair_chart,
            ses_data=widgets.fixed(ses_data),
            ses_metric=sorted(ses_data.keys()))

    with child23[0]:
        display(sensor_widget)

    with child23[1]:
        display(aqi_widget)

    return
