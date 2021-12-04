import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from sklearn import metrics
from statsmodels.tsa.statespace.sarimax import SARIMAX


def run_model(results, df_preds_, neighborhood, ts, order, seasonal_order, logged):
    
    '''
    This function runs a SARIMAX model with the specified order for a given neighborhood.
    Inputs:
        - results: dataframe, with rows for each neighborhoods, that stores the model, the order,
                   seasonal order, variance, MAE, MSE, R2, 2021 actual, 2021 predicted, and delta
        - df_preds_: dataframe to store the predictions through October 2021, with neighborhoods as column
        - ts: the time series to model. Should be the neighborhood-level dataframe.
        - order: the pdq order to use in the model
        - seasonal_order: the PDQ order to use in the model
        - logged: boolean for whether or not the train the model on the log transformed data
    Returns:
        - the results and prediction dataframes
    '''
    
    train = ts[ts['future'] == 0]
    test = ts[ts['future'] == 1]

    
    if logged:
        sari_model = SARIMAX(train['ride_count_log'], order=order, seasonal_order=seasonal_order).fit(maxiter=1000, disp=False)
    else:
        sari_model = SARIMAX(train['ride_count'], order=order, seasonal_order=seasonal_order).fit(maxiter=1000, disp=False)
    
    # Add preds to predictions DataFrame
    preds = sari_model.forecast(steps = len(test))
    if logged:
        df_preds_.loc[:,neighborhood] = np.exp(preds)
    else:
        df_preds_.loc[:,neighborhood] = preds
    
    # Retrieve metrics
    if logged:
        model_results = report_metrics(test['ride_count_log'], preds, False)
    else:
        model_results = report_metrics(test['ride_count'], preds, False)
    
    # Calculate actual vs. predicted rides for 2021
    actual_rides_2021 = ts[ts.index > '12/31/2020']['ride_count'].sum()
    pred_rides_2021 = df_preds_[df_preds_.index > '12/31/2020'][neighborhood].sum()
    
    ride_delta = np.abs(pred_rides_2021 - actual_rides_2021)
    
    # Add results to results dataframe
    results.loc[neighborhood, 'model'] = sari_model
    results.loc[neighborhood, 'order'] = order
    results.loc[neighborhood, 'seasonal_order'] = seasonal_order
    results.loc[neighborhood, 'explained_variance'] = model_results[0]
    results.loc[neighborhood, 'MAE'] = model_results[1]
    results.loc[neighborhood, 'MSE'] = model_results[2]
    results.loc[neighborhood, 'R2'] = model_results[3]
    results.loc[neighborhood, '2021_actual'] = actual_rides_2021
    results.loc[neighborhood, '2021_predicted'] = pred_rides_2021
    results.loc[neighborhood, 'delta'] = ride_delta
    
    return results, df_preds_


def neighborhood_grid_search(pdq, seasonal_pdq, neighborhood, df, df_grid_search):
    
    '''
    This function performs a grid search on each of the neighborhoods.
    
    Inputs:
        - pdq: list of pdq combinations to use during the grid search
        - seasonal_pdq: list of seasonal PDQ combinations to use during the grid search
        - neighborhood: the neighborhood to be modeled
        - df: the neighborhood df
        - df_grid_search: dataframe to store the grid search results. The index should be all the neighborhoods
                          to be modeled while the columns should be best AIC, best order, best seasonal order
                          
    Outputs:
        - Performs grid search and returns grid search dataframe with best results
    '''
    
    # Set ev to initial value of -1
    best_ev = -1
    
    print(f"Currently working on: {neighborhood}")
    
    train = df[df['future'] == 0]
    test = df[df['future'] == 1]

    for param in pdq:
        for param_seasonal in seasonal_pdq: 
            mod = SARIMAX(train['ride_count_log'], order=param, seasonal_order=param_seasonal).fit(maxiter=1000)
            
            forecast = mod.forecast(steps = len(test))
            # Even though the model is trained on logged data, we want to optimize the EV
            # on the unlogged version as we're trying to explain actual ridership
            ev = metrics.explained_variance_score(np.exp(test['ride_count']), np.exp(forecast))

            if ev > best_ev:
                best_ev = ev
                best_order = param
                best_s_order = param_seasonal
                df_grid_search.loc[neighborhood,:] = [best_order, best_s_order, best_ev]
    
    return df_grid_search


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

    '''
    Plots results of a time series model, specifically: train actuals, test actuals, and predicted results.
    Inputs:
        - Full, original dataframe (this will include both train and test data)
        - Predictions from holdout Test set
        - logged: boolean for whether the logged values were modeled. If True, values are unlogged before plotting
    Returns:
        - Plot of full time series broken out by Train actuals, Test actuals, and Test preds
    '''

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