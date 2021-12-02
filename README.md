# Citibike Ridership Prediction
Author: Jeff Marvel

## Overview

Citibike, NYC's bikeshare program owned and operated by Lyft, has become massively popular. With over 1,000 stations in almost every borough (sorry Staton Island) plus downtown Jersey City, Citibike has become an indispensable part of NYC's transportation infrastructure. Thousands of people rely on Citibike for their daily commuting, moving around their neighborhood, or helping bridge any gaps left by traditional city transportation infrastructure (subway, buses, etc).

While the city-wide lockdown in March of 2020 for the COVID-19 pandemic resulted in a sharp decrease in Citibike usage, ridership has more than bounced back in 2021 and is on pace for a record-breaking year. With two months still to go, 2021 ridership has already topped 24 million rides, breaking the previous record of 21 million from 2019. Given it's growth in popularity, which shows no signs of slowing, it's important to be able to accurately forecast ridership for the system overall, and also for each neighborhood in NYC.

For this project, my main goals are to build an accurate forecast for 2022 expected ridership overall, and by NYC neighborhood.

## Navigating the Repository

The main folder contains all the scripts and support needed to run the analysis from end to end.
* environment.yml contains the libraries and versions used for this project
* util.py contains functions for processing, testing, and evaluating models that are re-used throughout
* There are jupyter notebooks each for (1) reading in / processing data (2) EDA and (3) modeling. Notebooks should be run in the following order:
  * (1) citibike_data_import.ipynb
  * (2) citibike_eda.ipynb
  * (3) citibike_modeling.ipynb
* The "notebooks" folder contains backup sometimes referenced in the main folder for grid searches or other extra analyses that didn't make the final notebook cut.

## Accessing Data

* Ride-level data is provided by Citibike at the following ULR (https://s3.amazonaws.com/tripdata/index.html)
* It contains 130mm_ individual rides from the past 8 years with standard fields including origin station, destination station, station coordinates, start time, stop time, user type (member or guest), bike ID, and user gender
* All monthly CSV files should be saved in a folder at the main directory level called "ridership_raw"
* Important notes:
  * CSV files that begin with JC (Jersey City) should be ignored
  * Aggregated files (e.g., 201307-201402-citibike-tripdata.zip) should be ignored
  * The model is only trained on monthly data through October 2021. While my intent is to keep this updated as new data comes out, data should only be saved down up through the date listed in this README
* NYC geo_json data can be downloaded here (https://data.cityofnewyork.us/City-Government/2010-Neighborhood-Tabulation-Areas-NTAs-/cpf4-rkhq), just make sure to download as a GeoJSON file type.
* COVID recovery-related data can be found and downloaded here (https://www.investopedia.com/new-york-city-nyc-economic-recovery-index-5072042)

## Data Cleaning

* Citibike performs a few basic data cleaning steps before publishing the data:
  * Removes rides taken by staff to move bikes around or test the system
  * Rides to / from test stations (primarily relevant in 2013)
  * Rides under 60 seconds. These potentially represent users re-docking a broken bike or users ensuring that a particular bike is securely docked
* In order to trim the data to a size that can be run locally, I processed the data further by aggregating by day and unique station. For simplicity, several fields were dropped inclduing destination station and member type.
* Neighborhood and Borough were appended using the geo json file listed in "Accessing Data"

## Modeling

The main models leverage Statsmodels ARIMA and SARIMAX time series forecasting toolkits. I ran grid searches on the overall data plus for each NYC neighborhood with the goal of optimizing performance on the holdout (test) set to generate accurate 2022 predictions.

A key next step for this model (hopefully to be incorporated shortly) is to add exogenous variables in an attempt to control for the effect of the COVID-19 pandemic on ridership.

## Results

The final overall model achieved Explained Variance of 85% and an R2 of 83%, even when training on COVID data (which will potentially skew results). Neighborhood level models had a range of accuracies, but were generally quite accurate.

I project that Citibike will finish 2021 with a total of 27mm rides taken, a record. A predict they will break this record in 2022 with 31.3mm rides taken.
