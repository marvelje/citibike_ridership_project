import pandas as pd 
import numpy as np
from statsmodels.tsa.stattools import adfuller


def process_neighborhood(df, neighborhood):
    '''
    Creates a resampled 1D times series for the specified neighborhood.
    Backfills values for the ~10 dates that are missing
    Inputs:
        - Full dataframe
        - Neighboorhood
    Returns:
        - Time series of ridership for that neighborhood
    '''
    
    # Slice dataframe based on neighborhood name
    neighborhood_df = df[df['neighborhood'] == neighborhood]
    
    # Resample for one day intervals
    neighborhood_daily = neighborhood_df[['ride_count']].resample('1D').sum()
    
    # Backfill the handful of dates with missing ridership
    neighborhood_daily['ride_count'] = neighborhood_daily['ride_count'].replace(to_replace=0, method='bfill')
    
    return neighborhood_daily


def dickey_fuller(ts, plot_log, print_output):
    
    '''
    Tests a time series for stationarity using the Dickey Fuller test.
    Inputs:
        - ts: time series for testing
        - plot_log: boolean to log transform the time series
        - print_output: boolean to print the results or not
    Returns:
        - Boolean for stationary or not
        - P value from the test
    '''
    
    if plot_log:
        dftest = adfuller(np.log(ts))
    else:
        dftest = adfuller(ts)

    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic', 'p-value', '#Lags Used',
                                             'Number of Observations Used'])
    for key,value in dftest[4].items():
        dfoutput['Critical Value (%s)'%key] = value
        
    if dfoutput['p-value'] > 0.05:
        if print_output:
            print(f"Data is not stationary. P-value of {dfoutput['p-value']:.4f}")
        stationary = False
    else:
        if print_output:
            print(f"Data is stationary. P-value of {dfoutput['p-value']:.4f}")
        stationary = True
        
    return stationary, dfoutput['p-value']


def adjust_length(lst):
    '''
    Add 0s to the beginning of lists until it's the appropriate length.
    Used to make the queens and bronx ride lists are the same size as Manhattan / Brooklyn
    E.g., Bronx doesn't have any citibike rides until 2020. Adds 0s to ensure the list
    is the same length as the others for purposes of visualization.
    '''
    while len(lst) < 9:
        lst.insert(0, 0)
        
    return lst