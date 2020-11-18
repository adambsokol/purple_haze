# Functional Specification

### Background

It has been established that air pollution and health effects associated with it disproportionately affect poorer people and some racial and ethnic groups. With the advent of the PurpleAir air quality monitoring network in 2015, a variety of consumers within the governmental, industry, and educational sectors as well as citizen scientists and home enthusiasts have been able to record and share localized air quality data. PurpleAir air quality sensors are relatively cheap (~$250), providing more localized, more current, though less accurate readings compared to AirNow, an air quality network managed through the partnership of multiple government entities. Seattle’s PurpleAir network has expanded with the occurrence of wildfire smoke the past few years. Purple Haze is an analysis project to answer the following questions:

1. Is the distribution of PurpleAir sensors in Seattle equitable?
2. Are people of disadvantaged socioeconomic status disproportionately affected by poor air quality?

### User Profile

Our primary user is a researcher. The researcher will use our package to easily interface with both datasets and uncover relationships between combined metrics. The researcher is a proficient user of Jupyter Notebook and can program in Python. 

### Data Sources

#### PurpleAir
PurpleAir is an air quality monitoring network maintained by their low-cost air quality monitors purchased by organizations, citizen scientists, and home enthusiasts. PurpleAir air quality monitors use laser counters to measure particulate matter in real time. As a single particle passes through a laser, some of scattered laser light off of the particle will hit a detection plate, where the length of the laser light pulse determines particle size and the number of laser light pulses determines particle counts. Some assumptions in particle density and shape are employed to convert laser pulse length to particle mass concentration. The PurpleAir air quality monitor uses two lasers for data output, Channel A and Channel B, to ensure air quality measurements are precise.

For each PurpleAir air quality monitor, which we will now refer to as "sensor," the data is available as four separate CSV files named with the following format: ``Sensor Name _ (Location) (Latitude Longitude) Order #_minute_average mm_dd_yyyy mm_dd_yyyy.csv`` where:
* Sensor Name is an owner-named property
* _ is used to designate the laser channel, either left blank for Channel A or `B` for Channel B
* Location is `outside`, `inside`, or `undefined` 
* Latitude is the sensor's latitude in degrees
* Longitude is the sensor's longitude in degrees
* Order is `Primary` or `Secondary`
* \# is the number of minutes averaged
* The first mm_dd_yyyy is the data start date
* The second mm_dd_yyyy is the data end date

The four CSV files are created as the following pairs:
1. Channel A and Primary
2. Channel A and Secondary
3. Channel B and Primary
4. Channel B and Secondary

Primary files contain the following variables, where CF denotes indoor/controlled (1) or outdoor (ATM) particle densities:
* Creation time (yyyy-mm-dd hh:mm:ss UTC)
* PM1.0 (CF=1) (ug/m3)
* PM2.5 (CF=1) (ug/m3)
* PM10.0 (CF=1) (ug/m3)
* Uptime (Minutes)
* RSSI (WiFi Signal Strength)
* Temperature (F)
* Humidity (%)
* PM2.5 (CF=ATM) (ug/m3)

Secondary files contain the following variables:
* Creation time (yyyy-mm-dd hh:mm:ss UTC)
* 0.3um (particles/deciliter)
* 0.5um (particles/deciliter)
* 1.0um (particles/deciliter)
* 2.5um (particles/deciliter)
* 5.0um (particles/deciliter)
* 10.0um (particles/deciliter)
* PM1.0 (CF=ATM) (ug/m3)
* PM10 (CF=ATM) (ug/m3) 

For our analysis project, we chose to include all PurpleAir sensors located and operating within Seattle from May 1 to November 1, 2020 and chose our output as 60-minute averaged data.

Source: https://www.purpleair.com/map

#### Seattle's Racial and Social Equity Composite Index
Seattle is a city with an Open Data Program, a program whose purpose is to make data created by the city of Seattle publicly accessible. One of these publicly available datasets is the Racial and Social Equity Composite Index (RSECI). Information on race, ethnicity, and other demographics are combined with socioeconomic and health disadvantages data to locate where priority populations are residing. 

The following demographic, socioeconomic, and health metrics are provided by the city of Seattle at the census tract level:
* Adults diagnosed with diabetes (percent and percentile)
* Adults that are obese (percent and percentile)
* Adults with asthma (percent and percentile)
* Adults with disabilities (percent and percentile)
* Adults with no leisure-time physical activity (percent and percentile)
* Adults with poor mental health (percent and percentile)
* Composite Index (percentile and quintile)
* Educational attainment less than a bachelor's degree (percent and percentile)
* English language learner (percent and percentile)
* Foreign born (percent and percentile)
* Health Index (percentile and quintile)
* Income below 200 percent of poverty (percent and percentile)
* Low life expectancy at birth (percent and percentile)
* People of color (percent and percentile)
* Race, English Language Learners Index (percentile and quintile)
* Socioeconomic Index (percentile and quintile)

This data is provided in a variety of formats (e.g. GeoJSON, CSV, KML, shapefile, etc.), but for this analysis project, we have chosen to use shapefile output due to its ease of use with producing visualizations of Seattle's census tracts. The file can be downloaded as a .zip folder containing 5 files to make up the shapefile: a .cpg file containing the codepage information, a .dbf file storing the RSECI metrics for each census tract, a .prj file storing the coordinate system information, a .shp file containing the census tract geometry, and a .shx file containing the census tract indexing.

Source: https://data.seattle.gov/dataset/Racial-and-Social-Equity-Composite-Index/da35-mm5v

### Use Cases

#### Use Case 1: Find the number of PurpleAir sensors within a census tract in Seattle.
* The user will be able to look at our visualization to get a broad sense of PurpleAir sensor distribution among the census tracts. 
* The user will be able to use Python with the Jupyter Notebook to make inquiries within our GeoPandas dataframe.

#### Use Case 2: Compute the PM2.5 and AQI averages for each census tract in Seattle.
* The user will hover over a census tract in our visualization and will generate a tooltip containing census identification, summary statistics of PM2.5 and AQI, and the Composite Index for that census tract.
