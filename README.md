# Purple Haze

[![Build Status](https://travis-ci.org/adambsokol/purple_haze.svg?branch=main)](https://travis-ci.org/adambsokol/purple_haze)
[![Coverage Status](https://coveralls.io/repos/github/adambsokol/purple_haze/badge.svg?branch=main)](https://coveralls.io/github/adambsokol/purple_haze?branch=main)

### A Local Urban Investigation on the Correlation Between Air Quality, Demographics, and Socioeconomic and Health Disadvantages

It has been established that both short-term and long-term exposure to poor air quality can have serious health effects. Air quality, and its health effects, are not distributed homogenously across the city of Seattle, and disproportionately harm people of color and those of lower socioeconomic status due to past and current societal inequities. With the advent of the PurpleAir air quality monitoring network in 2015, a variety of consumers within the governmental, industry, and educational sectors as well as citizen scientists and home enthusiasts have been able to record and share localized air quality data. PurpleAir air quality sensors are relatively cheap (~$250), providing a more localized and real-time, though less accurate compared to AirNow, air quality network. Seattle’s PurpleAir network has expanded with the occurrence of wildfire smoke the past few years, particularly in the summer and fall of 2020. Purple Haze is an analysis project to answer the following questions: 

1. Is the distribution of PurpleAir sensors in Seattle equitable? 
2. Are people of disadvantaged socioeconomic status disproportionately affected by poor air quality as measured by PurpleAir sensors?

### Team Members

* Tyler Cox
* Carley Fredrickson
* Greta Shum
* Adam Sokol

### Software dependencies and license information
All first-level software dependencies are listed in the environment.yml file. This does not include all software dependencies as many of the listed packages have their own dependencies. <br>
This package is licensed under the MIT license which allows generally free and open use, in-line with our desire for this software to be used by whomever may find it useful.

### Installation
To install and run this locally do the following: <br>
0. install conda if you have not already done so
1. clone the repository: git clone https://github.com/adambsokol/purple_haze.git
2. create a conda environment for this project: conda env create -q -n purple_haze --file environment.yml
3. activate the environment: conda activate purple_haze
4. if using jupyter lab see 4a/b, otherwise skip to 5 <br>
4a. install a few Jupyterlab extensions. You can either run the shell script: bash lab_extensions.sh (Note, that if running on Windows you may need to do the following command:<br>
tr -d '\r' < lab_extensions.sh > new_lab_extensions.sh<br>
Then run the new_lab_extensions.sh file. <br>
4b. or you can do it manually be running the following in the command line: <br>
        jupyter labextension install @jupyter-widgets/jupyterlab-manager --no-build <br>
        jupyter labextension install @jupyter-voila/jupyterlab-preview --no-build <br>
        jupyter lab build <br>
5. to simply view the data, in the command line run: voila purple_haze/purple_haze_app.ipynb --no-browser
6. then launch your corresponding local host in a web browser. Typically this means going to the site 'localhost:8866'
7. if you want to explore the data in more detail you can launch jupyter and open purple_haze_app.ipynb

Video examples of running the dashboard can be found in `examples/`. As shown below, Voila displays our application, with instructions provided at the top. The dashboard contains an interactive choropleth map with the ability to download images as well as two interactive scatterplot to facilitate analysis. In each, the data is linearly regressed and the coefficient of determination is printed on the figure. 

![Dashboard demo showing choropleth map and two scatterplots combining PurpleAir and City of Seattle data](examples/dashboard.png?raw=true "Dashboard Example")

### Directory Summary
The directory has appropriately named data, docs, and example folders. Project code lies in the purple_haze directory. The purple_haze_app.ipynb lies in the purple_haze folder as it provides the core of the code that allows the data to display using Voila.

### Directory Structure

```
purple_haze/
   |- data/
      |- purple_air/
         |- ...
      |- seattle_ses_data/
         |- ...
   |- docs/
      |- Technology Review.pptx
      |- component_specification.md
      |- functional_specification.md
   |- examples/
      |- dashboard.png
      |- demo.mp4
      |- demo_part1.mp4
      |- demo_part2.mp4
   |- purple_haze/
      |- __init__.py
      |- air.py
      |- figures.py
      |- matcher.py
      |- purple_haze_app.ipynb
      |- tests/
         |- __init__.py
         |- test_ph.py
   |- .travis.yml
   |- LICENSE
   |- README.md
   |- environment.yml
   |- lab_extensions.sh
   |- setup.py
```

### Project Data
##### PurpleAir data <br>
-Includes only sensors in or near Seattle <br>
-Time series of PM2.5 concentrations from May 1st to Nov. 1st 2020 <br>
-60 minute averaged data <br>
-Source: https://www.purpleair.com/map

##### Socioeconomic data <br>
-Census level data within Seattle <br>
-Includes demographic, socioeconomic, and health metric data <br>
-Source: https://data.seattle.gov/dataset/Racial-and-Social-Equity-Composite-Index/da35-mm5v

### Air Quality Metric Calculation
Each hourly PM2.5 measurement from the Purple Air dataset is used to compute the hourly Air Quality Index (AQI). AQI is calculated using the EPA formula (see https://www.airnow.gov/sites/default/files/2018-05/aqi-technical-assistance-document-may2016.pdf). <br>

Hourly AQI measurements from outdoor Purple Air sensors are then used to calculate several air quality metrics for each sensor-containing census tract:
* *mean_aqi*: the average AQI for the census tract. If there are multiple sensors in a tract, the sensor-mean AQI is first calculated at each hour of the data record, and then the time-mean AQI is calculated for the whole tract.
* *mean_aqi_no_smoke*: as above, but not including measurements between 00:00 UTC on 2020-09-08 and 23:00 UTC on 2020-09-19, when thick wildfire smoke covered Seattle. Because the smoke produced very high AQI across the region, it may mask any underlying correlations between AQI and different socioeconomic metrics.
* *exposure_aqi100* (*exposure_aqi150*): the average amount of time that AQI in a census tract exceeds 100 (150), expressed in minutes per week. This is calculated finding the total number of hourly AQI measurements in the tract that exceed the AQI threshold (across all otutdoor sensors) and dividing by the total number of valid, outdoor, hourly AQI measurements in the tract. Units are then converted to minutes per week.
* *exposure_aqi100_no_smoke* (*exposure_aqi150_no_smoke*): as above, but not including measurements between 00:00 UTC on 2020-09-08 and 23:00 UTC on 2020-09-19.

### Project History
Project conducted October through December 2020 as part of CSE 583 at the University of Washington.

###  Limitations
The data in this project is not continuously updating, and the repository will not necessarily be maintained beyond December 2020.
