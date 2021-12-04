import pandas as pd
from shapely.geometry import Point, Polygon, shape
import geopandas as gpd
import json
import numpy as np

def pre_process(df):
    
    '''
    Processing a dataframe of individual ride data by performing the following steps:
    - Converts start time to dataype datetime and set it as the index
    - Group the data by 1D frequency, include start station id, latitude, longitude
    - Aggregate data by count
    - Rename "count" column "ride_count"
    - Reset the index then move starttime back to the index (removes multi-index layers)
    '''
    
    df['starttime'] = pd.to_datetime(df['starttime'])
    
    df = df.set_index('starttime')
    
    grouper = df.groupby([pd.Grouper(freq='1D'), 'start station id', 'start station latitude', 'start station longitude'])
    
    df_grouped = pd.DataFrame(grouper['start station id'].count())
    
    df_grouped = df_grouped.rename(columns={'start station id': 'ride_count'})
    
    df_grouped = df_grouped.reset_index().set_index('starttime')
    
    return df_grouped


def pre_process_2021(df):
    
    '''
    Same as other processing function except customized slightly given ride share data in 
    2021 has different column names
    
    Processing a dataframe of individual ride data by performing the following steps:
    - Converts start time to dataype datetime and set it as the index
    - Group the data by 1D frequency, include start station id, latitude, longitude
    - Aggregate data by count
    - Rename "count" column "ride_count"
    - Reset the index then move starttime back to the index (removes multi-index layers)
    - Renaming rest of columns to match previous version
    '''
    
    df['starttime'] = pd.to_datetime(df['started_at'])
    
    df = df.set_index('starttime')
    
    grouper = df.groupby([pd.Grouper(freq='1D'), 'start_station_id', 'start_lat', 'start_lng'])
    
    df_grouped = pd.DataFrame(grouper['start_station_id'].count())
    
    df_grouped = df_grouped.rename(columns={'start_station_id': 'ride_count'})
    
    df_grouped = df_grouped.reset_index().set_index('starttime')
    
    df_grouped['start_station_id'] = df_grouped['start_station_id'].apply(lambda x: convert_station(x))
    
    df_grouped.rename(columns={'start_station_id': 'start station id', 
                             'start_lat': 'start station latitude', 
                             'start_lng': 'start station longitude'}, inplace=True)
    
    return df_grouped


def neighborhood_json(point):
    '''
    Function accepts a Point object from the shapely library.
    It parses through the JSON of nyc neighborhood geo data, checking if any of them contain the point.
    If there is a match, the neighborhood name is returned.
    
    '''
    for feature in nycmap['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            return feature['properties']['ntaname']
            continue

def borough_json(point):
    '''
    This is a repeat of the function above, except to return borough instead of neighborhood.
    
    Function accepts a Point object from the shapely library.
    It parses through the JSON of nyc neighborhood geo data, checking if any of them contain the point.
    If there is a match, the borough name is returned.
    
    '''
    for feature in nycmap['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            return feature['properties']['boro_name']
            continue