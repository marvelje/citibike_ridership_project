# Citibike Ridership Prediction
Author: Jeff Marvel

## Overview and Business Problem

Citibike, NYC's bikeshare program owned and operated by Lyft, has become massively popular. With over 1,000 stations in almost every borough (sorry Staton Island) plus downtown Jersey City, Citibike has become an indispensable part of NYC's transportation infrastructure. The NYC sponsored [feasibility study](https://www1.nyc.gov/assets/planning/download/pdf/plans/transportation/bike_share_complete.pdf) for Citibike's launch cites how NYC is an ideal location for a bikeshare program given its population density. Bikeshare programs offer transportation solutions that can be deployed within a matter of months as opposed to years (or even decades) for alternatives such as bus lines or subways. Among the benefits anticipated by the study (which performed an exhaustive review of existing bikeshare programs) are increased trasnportation options for NYC commuters, residents, and tourists, better health outcomes, and pollution / carbon reduction.

Another NYC sponsored [study](https://www1.nyc.gov/html/dot/html/bicyclists/bike-ridership-safety.shtml) argues that bikeshare programs lead to materially improved safety for all cyclists, given increased visibility of cyclists on the street (drivers are more acclimated to seeing cyclists), and improved bicycle infrastructure. After 135mm rides taken since launch, there have only been two Citibike related deaths. Also, at the time of this [writing](https://ride.citibikenyc.com/blog/100million) for Citibike's 100 millionth ride, the program was estimate to have reduced carbon emissions by 97mm pounds. 

The growth in ridership over the last 8 years has proven many of the anticipated benefits of the system. Ridership continues to set records: with two months to go in 2021, rides have already topped 24 million, up from the previous record of 21mm in 2019 (ridership in 2020 suffered a decrease related to the COVID-19 pandemic). This growth has started to cause strains on the system, per [this](https://ride.citibikenyc.com/blog/ridershiprecords) Citibike blog post celebrating ridership records this year. Given its continued growth and its many documented benefits, it's important to be able to accurately forecast ridership for the system to help Citibike successfully meet this demand.


## Previous Research

Given that Citibike freely publishes their ridership data, it's no surprise that other people have tackled this forecasting challenge. Additionally, there is extensive literature on bike share programs more generally as their popularity has soared. Inspiration for this project include:
* A [Kaggle](https://www.kaggle.com/c/bike-sharing-demand) competition for predicting bike share demand in Washington DC
* [This](https://towardsdatascience.com/analysis-and-prediction-of-citi-bike-usage-in-the-unpredictable-2020-3401da26881b) thorough blog post forecasting Citibike ridership using linear regression
* A [research paper](https://nacto.org/wp-content/uploads/2015/07/2012_Rixey_Station-Level-Forecasting-of-Bike-Sharing-Ridership.pdf) on key exogenous factors that drive bike share ridership

I will differentiate my project by training on the most recent Citibike data using SARIMAX time series modeling techniques, as well as exploring controls for the effects of the COVID-19 pandemic on ridership.

## Project Goals

There are two main goals for this project:
* Predict overall ridership levels for 2022 (including total rides and peak ridership)
* Predict neighborhood-level ridership totals for 2022 (total growth and percent growth)

The output of this model can be used to ensure sufficient system capacity to meet this demand, and plan for additional stations in high growth neighborhoods.

## Accessing Data

* Ride-level data is provided by Citibike [here](https://s3.amazonaws.com/tripdata/index.html)
* It contains 130mm+ individual rides from the past 8 years with standard fields including origin station, destination station, station coordinates, start time, stop time, user type (member or guest), bike ID, and user gender
* Clicking on the zips will download the monthly ridership CSV. All monthly CSV files should be saved in a folder at the main directory level called "ridership_raw"
* Important notes:
  * CSV files that begin with JC (Jersey City) should be ignored
  * Aggregated files (e.g., 201307-201402-citibike-tripdata.zip) should be ignored
  * The model is only trained on monthly data through October 2021. While my intent is to keep this updated as new data comes out, data should only be saved down up through the date listed in this README
* NYC geo_json data can be downloaded [here](https://data.cityofnewyork.us/City-Government/2010-Neighborhood-Tabulation-Areas-NTAs-/cpf4-rkhq), just make sure to download as a GeoJSON file type. This should be saved in a folder in the main directory called "nyc_geo_data"
* COVID recovery-related data can be found and downloaded [here](https://www.investopedia.com/new-york-city-nyc-economic-recovery-index-5072042). The csv should be saved in a folder in the main directory named "covid_data".

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

The final overall model achieved Explained Variance and R2 of 83%, even when training on COVID data (which will potentially skew results). Neighborhood level models had a range of accuracies, but over 2/3 achieved Explained Variance scores greater than 50%. In other words, the overall model predictions could explain ~83% of the change in ridership of the holdout test set.

I project that Citibike will finish 2021 with a total of 27mm rides taken, a record. This record is forecast to be broken in 2022 with 34mm rides taken. 

The neighborhoods expected to have the highest growth in total ridership are all in Midtown Manhattan, which isn't surprising given how much growth they've experienced recently. The highest percent growth neighborhoods are potentially more interesting. The fastest growing neighborhoods are all near Prospect Park in Brooklyn, including Sunset Park, Park Slope / Gowanus, and Prospect heights.

I did incorporate COVID controls as an additional step. Using the NYC recovery index (referenced earlier), I built several lockdown scenarios. A mild lockdown to start 2022 could reduce peak summer ridership by 14% while a Severe Lockdown (similar to March 2020) could reduce peak ridership by 21%.

## Conclusion / Next Steps

I was able to build a time series model that performed very well on the holdout data. The main downside of this model is that it produces an aggressive 2022 forecast. While this feels appropriate given the trends in the data, it's unclear whether Citibike has the capacity to meet this demand. As mentioned in the introduction, ridership at current levels is causing strains on the system. An additional 7mm rides in 2022 may be a tall order. On the other hand, Citibike continues to add stations and capacity, so maybe the system could absord this growth after all. Citibike should focus on aggressively building bike inventory and increasing the number of stations available, particularly in the high growth neighborhoods cited previously.

Next steps:
* I want to further tune the neighborhood models by incorporating controls for COVID. There's definitely room to improve the EV of these models. 
* I'd also like to explore more granular versions of the Citibike data, including looking at intra-day time periods and shorter-term projections. This can be used to build models that describe daily commuting and general use patterns, and can help inform more tactical, daily planning / decisions.

## Navigating the Repository
```
├── support_notebooks                        <- Additional backup referenced for the main analyses (e.g., grid searches, other modeling iterations)
│   ├── citibike_arima.ipynb                 <- Overall modeling iterations
│   ├── citibike_arima_neighborhood.ipynb    <- Neighborhood-level modeling iterations
│   ├── citibike_data_consolidation.ipynb    <- Consolidating the processed data
│   ├── citibike_data_import.ipynb           <- Raw data import and processing
│   ├── citibike_sarimax.ipynb               <- SARIMAX model incorporating COVID independent variables
│   └── util.py                              <- Util file containing functions for these support notebooks
│
├── util                                     <- Contains notebook-specific utility files / scripts
│   ├── __init__.py                          <- Requisite empty init py file
│   ├── eda_util.py                          <- Functions used in EDA
│   ├── modeling_util.py                     <- Functions used in modeling prep / evaluation
│   └── preprocess_util.py                   <- Functions used in reading / processing data
│
├── .gitignore                               <- Standard python gitignore file with additional data / MAC specific ignore commands
├── README.md                                <- Project summary, including instructions for accessing and processing the data
├── citibike_data_import.ipynb               <- Script to read in and process the raw ridership files
├── citibike_eda.ipynb                       <- Script to perform EDA, including visualizations on the overall and neighborhood-level data
├── citibike_modeling.ipynb                  <- Main modeling notebook, includes main iterations for overall model and neighborhood models
└── environment.yml                          <- Environment file containing all libraries and versions to run this project
```
