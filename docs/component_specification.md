# Purple Haze - Component Specification

## Components

##### 1. Organizing Purple Air Data Files
We will use the term *sensor* to refer to a single Purple Air monitoring unit that can be purchased by any member of the public and stationed in any indoor or outdoor location. The data from each sensor is spread across four CSV files; we will refer to the data within each of these files as a *data stream*. The four data streams are:
1. Channel A (Primary)
2. Channel A (Secondary)
3. Channel B (Primary)
4. Channel B (Secondary)

All of the CSV files for this project are kept in a single directory (i.e., they are not organized by sensor). The purpose of this component is to retrieve the lat/lon coordinates and location (indoors or outdoors) for each data stream and to assign each data stream to its correct census tract. The pieces of information needed to accomplish this can all be obtained from the CSV file names themselves (reading the files is not necessary) and the census tract shape files. 

**Inputs**: list of CSV file paths; paths to census tract shape files

**Outputs**: single geopandas dataframe containing socioeconomic data and data stream file paths for each census tract

##### 2. Reading & Analyzing Purple Air Data
This component reads and manipulates air quality data once the data streams have been organized by census tract. This includes:
- matching the four data streams from each sensor and combining their data
- determining which data variables are to be used for analysis (this depends on whether the sensor is indoors or outdoors)
- calculating Air Quality Index (AQI)
- combining data from all of the sensors located within a single census tract
- calculating air quality statistics for each census tract, including mean AQI and mean AQI without the 2020 wildfire smoke event

**Inputs**: geopandas dataframe containing socioeconomic data and data stream file paths for each census tract

**Outputs**: the input dataframe with added air quality statistical variables for each census tract

##### 3. Visualization
The visualization component allows users to access and understand the data in a meaningful way. This component aims to do the following:
- Determine and display how the number of sensors in a census tract is related to the racial and socioeconomic composition of the census tracts sharing the same number of sensors
- Determine and display how the air quality statistic of a census tract is related to the racial and socioeconomic composition of that census tract
- Output a census tract map of Seattle colored by a user-specified socioeconomic, demographic, or health metric

**Inputs**: geopandas dataframe containing socioeconomic data and air quality statistics for each census tract calculated from Purple Air sensors

**Outputs**: a variety of plots, with optional user input, in a Jupyter notebook to explore relationships between the number of Purple Air sensors within census tracts, air quality data, and socioeconomic data

## Interactions

##### 1. User can select via dropdown which socioeconomic metric they would like to use in the choropleth map and both scatter plots. This metric will then be regressed against number of PurpleAir sensors and air quality data by census tract and displayed with appropriate plots. This requires interaction between all three components.

##### 2. The user can hover over a map of Seattle to get census tract number. This requires only our visualization component (#3).

##### 3. User can select which air quality statistical variable they would like to use in the lower scatter plot chart. This metric will then be regressed against the user-selected socioeconomic metric and displayed with appropriate appropriate plots. This requires interaction between our data analysis component (#2) and our visualization component (#3).

## Preliminary Plan
 1. Implement thorough testing using unittest. 
 2. Improve map by adding additional tooltips (number of sensors in a census tract, etc).
 3. Improve visualization for readability in labels.
 
