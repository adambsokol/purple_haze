# Purple Haze - Component Specification

## Components

##### 1. Organizing Purple Air Data Files
We will use the term *sensor* to refer to a single Purple Air monitoring unit that can be purchased by any member of the public and stationed in any indoor or outdoor location. The data from each sensor is spread across four CSV files; we will refer to the data within each these file as a *data stream*. The four data streams are:
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
- calculating air quality statistics for each census tract

**Inputs**: geopandas dataframe containing socioeconomic data and data stream file paths for each census tract
**Outputs**: the input dataframe with added air quality statistical variables for each census tract

##### 3. Visualization
The visualization component allows users to access and understand the data in a meaningful way. This component aims to do the following:
- Determine and display how the average number of sensors in a census tract is related to the racial and socioeconomic composition of that census tract
- Determine and display how the average air quality of a census tract is related to the racial and socioeconomic composition of that census tract
- Provide the user with the option to view and explore the data using different racial and socioeconomic metrics

**Inputs**: geopandas dataframe containing socioeconomic data and air quality statistics for each census tract calculated from Purple Air sensors
**Outputs**: a variety of plots, with optional user input, in a Jupyter notebook to explore relationships between Purple Air sensor locations, air quality data, and socioeconomic data

## Interactions

##### 1. User can select which socioeconomic metric they would like to use. This metric will then be regressed against Purple Air sensors and air quality data by census tract and displayed with appropriate plots. 

##### 2. The user can hover over a map of Seattle and select data from a single census tract. This selection will then display socioeconomic data, quantity of Purple Air sensors, and air quality data for that census tract.

## Preliminary Plan
 - Determine visualization engine

 