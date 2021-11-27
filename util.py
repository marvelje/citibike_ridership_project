import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from sklearn import metrics

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

    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic', 'p-value', '#Lags Used', 'Number of Observations Used'])
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

def report_metrics(y_true, y_pred, print_output):
    '''
    Function to return basic summary statistics from the model.
    Inputs:
        - Actual y values (y_true)
        - Predicted y values (y_pred)
        - print_output: Boolean to display output in the terminal or not
    Returns:
        - List with Explain Variance, MAE, MSE, and R2
    '''
    ev = metrics.explained_variance_score(y_true, y_pred)
    mae = metrics.mean_absolute_error(y_true, y_pred)
    mse = metrics.mean_squared_error(y_true, y_pred, squared=False)
    r2 = metrics.r2_score(y_true, y_pred)
    
    if print_output:
        print(f"Explained Variance: {ev:,.4f}")
        print(f"MAE: {mae:,.4f}")
        print(f"RMSE: {mse:,.4f}")
        print(f"r^2: {r2:,.4f}")
    
    return [ev, mae, mse, r2]


def plot_results(df, preds, logged):
    fig, ax = plt.subplots(figsize=(10,6))
    
    if logged:
        # Training data
        df.loc[df.future == 0, 'ride_count'].plot(color='blue', label='actual train', ax=ax)
        # Predictions
        np.exp(preds).plot(color='green', label='predicted test', ax=ax)
        # Testing data
        df.loc[df.future == 1, 'ride_count'].plot(color='blue', label='actual train', ax=ax, alpha = 0.5)
    else:
        # Training data
        df.loc[df.future == 0, 'ride_count'].plot(color='blue', label='actual train', ax=ax)
        # Predictions
        preds.plot(color='green', label='predicted test', ax=ax)
        # Testing data
        df.loc[df.future == 1, 'ride_count'].plot(color='blue', label='actual train', ax=ax, alpha = 0.5)