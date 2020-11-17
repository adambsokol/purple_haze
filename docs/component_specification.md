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
Blah blah blah
**Inputs**: 
**Outputs**: 

## Interactions

##### 1. 

##### 2. 

## Preliminary Plan
 - Determine visualization engine

 