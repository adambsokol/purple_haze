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

### Installation
To install and run this locally do the following:
0. install conda if you have not already done so
1. clone the repository: git clone https://github.com/adambsokol/purple_haze.git
2. create a conda environment for this project: conda env create -q -n purple_haze --file environment.yml
3. activate the environment: conda activate purple_haze
4. if using jupyter lab see 4a/b, otherwise skip to 5 <br>
4a. install a few Jupyterlab extensions. You can either run the shell script: bash lab_extensions.sh <br>
4b. or you can do it manually be running the following in the command line: <br>
        jupyter labextension install @jupyter-widgets/jupyterlab-manager --no-build <br>
        jupyter labextension install @jupyter-voila/jupyterlab-preview --no-build <br>
        jupyter lab build <br>
5. to simply view the data, in the command line run: voila purple_haze_app.ipynb --no-browser
6. then launch your corresponding local host in a web browser. Typically this means going to the site 'localhost:8888'
7. if you want to explore the data in more detail you can launch jupyter and open purple_haze_app.ipynb

### Directory Summary
The directory has appropriately named data, docs, and example folders. Project code lies in the purple_haze directory.

### Directory Structure

The project has the following structure:

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
      |- Demo_part1_purple_haze_Trim.mp4
      |- Demo_part2_purple_haze_Trim.mp4
      |- Demo_purple_haze.mp4
   |- purple_haze/
      |- __init__.py
      |- air.py
      |- figures.py
      |- matcher.py
      |- purple_haze_app.ipynb
      |- test_modules.py
   |- .travis.yml
   |- LICENSE
   |- README.md
   |- __main__.py
   |- environment.yml
   |- lab_extensions.sh
```

### Project Data
PurpleAir data <br>
-Includes only sensors in or near Seattle <br>
-Time series of PM2.5 concentrations from May 1st to Nov. 1st 2020 <br>
-60 minute averaged data <br>
-Source: https://www.purpleair.com/map

    
Socioeconomic data <br>
-Census level data within Seattle <br>
-Includes demographic, socioeconomic, and health metric data <br>
-Source: https://data.seattle.gov/dataset/Racial-and-Social-Equity-Composite-Index/da35-mm5v


### Project History
Project conducted October through December 2020 as part of CSE 583 at the University of Washington.

###  Limitations
The data in this project is not continuously updating, and the repository will not necessarily be maintained beyond December 2020.

### Acknowledgements
