import pandas as pd
import numpy as np
import datetime
from xml.etree import ElementTree
import xmltodict
from calculate_stats import avg_speed_2d

# ____________ Helper functions for parsing ____________

def haversine_np(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in feet between two points on the earth (specified in decimal degrees)
    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    dist = 3956 * 5280 * c
    return dist


def min_moving_speed(activity_type):
    MIN_MOVING_SPEEDS = {'cycling':2.5, 'running':2.0, 'swimming':0.1}
    if activity_type in MIN_MOVING_SPEEDS:
        return MIN_MOVING_SPEEDS[activity_type]
    else:
        return 0.01


def engineer_features(name, act_type, date, df, zones=[113, 150, 168, 187]):
    # 'time_delta' is elapsed time between successive points
    if 'time' in df.columns.values:
        df['time_delta'] = (df.time - df.time.shift(1)).apply(lambda x : x.total_seconds())
    # 'elevation_change' is change in elevation between successive points
    if 'elevation' in df.columns.values:
        df['elevation_change'] = df.elevation - df.elevation.shift(1)
    # define helper inner-function to calculate heart rate zones
    def calculate_zone(hr):
        if hr < zones[0]:
            return 1
        elif hr < zones[1]:
            return 2
        elif hr < zones[2]:
            return 3
        elif hr < zones[3]:
            return 4
        else:
            return 5
    if 'hr' in df.columns.values:
        # 'zone' is heart rate zone during that point
        df['zone'] = df.hr.apply(calculate_zone)
    if 'lon' in df.columns.values:
        # calculate 2d distances between consecutive points
        df['distance_2d_ft'] = haversine_np(df.lon.shift(),
                         df.lat.shift(),
                         df.ix[1:, 'lon'],
                         df.ix[1:, 'lat'])
        # calculate 3d distances between consecutive points
        df['distance_3d_ft'] = np.sqrt(df.distance_2d_ft**2 +
                         df.elevation_change**2)
        df['speed_2d'] = (df.distance_2d_ft/5280)/(df.time_delta/3600)
        df['speed_3d'] =     df['speed_2d'] = (df.distance_3d_ft/5280)/(df.time_delta/3600)
        df['moving'] = df.speed_2d >= min_moving_speed(act_type)
    return name, act_type, date, df


def impute_nulls(name, act_type, date, df):
    """
    Imputes mean of surrounding values in the column, and casts to same dtype as previous value in column. Ignores nulls in first/last rows.
    """
    nulls = df.isnull().unstack()
    nulls_ind = nulls[nulls].index.values
    for (col, row) in nulls_ind:
        if (row != 0) and (row != df.shape[0]):
            imputed_value = (df[col][row-1]+df[col][row+1])*0.5
            if type(df[col][row-1]) == float:
                df[col][row] = float(imputed_value)
            elif type(df[col][row-1]) == int:
                df[col][row] = int(imputed_value)
            elif type(df[col][row-1]) == type(np.float64(0)):
                df[col][row] = np.float64(imputed_value)
    return name, act_type, date, df


def correct_activity_type(act_type, df):
    if act_type == 'Unknown Activity Type':
        avg_speed = avg_speed_2d(df)
        if avg_speed > 10.0:
            act_type = 'cycling'
        elif avg_speed > 5.0:
            act_type = 'running'
        elif avg_speed > 1.5:
            act_type = 'hiking'
    return act_type, df


# ____________ Helper functions for parse_gpx() ____________

def unpack_gpx_trkpt(trkpt):
    trackpoint = {}
    try:
        trackpoint['time'] = datetime.datetime.strptime(trkpt['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        trackpoint['time'] = datetime.datetime.strptime(trkpt['time'], '%Y-%m-%dT%H:%M:%SZ')
    if '@lat' in trkpt:
        trackpoint['lat'] = float(trkpt['@lat'])
    if '@lon' in trkpt:
        trackpoint['lon'] = float(trkpt['@lon'])
    if 'ele' in trkpt:
        trackpoint['elevation'] = float(trkpt['ele'])
    if 'extensions' in trkpt:
        if 'ns3:TrackPointExtension' in trkpt['extensions']:
            ext = trkpt['extensions']['ns3:TrackPointExtension']
            if 'ns3:hr' in ext:
                trackpoint['hr'] = int(ext['ns3:hr'])
            if 'ns3:atemp' in ext:
                trackpoint['air_temp'] = float(ext['ns3:atemp'])
            if 'ns3:cad' in ext:
                trackpoint['cadence'] = int(ext['ns3:cad'])
        elif 'gpxtpx:TrackPointExtension' in trkpt['extensions']:
            ext = trkpt['extensions']['gpxtpx:TrackPointExtension']
            if 'gpxtpx:hr' in ext:
                trackpoint['hr'] = int(ext['gpxtpx:hr'])
            if 'gpxtpx:atemp' in ext:
                trackpoint['air_temp'] = float(ext['gpxtpx:atemp'])
            if 'gpxtpx:cad' in ext:
                trackpoint['cadence'] = int(ext['gpxtpx:cad'])
    return trackpoint


def extract_metadata_gpx(xmldict):
    if 'trk' in xmldict['gpx']:
        if 'name' in xmldict['gpx']['trk']:
            name = xmldict['gpx']['trk']['name']
        else:
            name = 'Unnamed Activity'
        if 'type' in xmldict['gpx']['trk']:
            act_type = xmldict['gpx']['trk']['type']
        else:
            act_type = 'Unknown Activity Type'
    else:
        act_type = 'Unknown Activity Type'
        name = 'Unnamed Activity'
    try:
        date = datetime.datetime.strptime(xmldict['gpx']['metadata']['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
    except:
        date = datetime.datetime.strptime(xmldict['gpx']['metadata']['time'], '%Y-%m-%dT%H:%M:%SZ')
        return name, act_type, date
    else:
        return None, None, None


def unpack_gpx(filepath):
    """
    Unpacks GPXTrack XML file constructed by Garmin device (currently tested for Forerunner 230 and Edge 810) containing a single GPX Track and Track Segment, or .gpx files for activities downloaded from Strava.

    Returns tuple of name, activity type, activity date (as datetime object), and dataframe containing observational data for each trackpoint.
    """
    list_of_trkpt_dicts = []
    with open(filepath, 'r') as f:
        dct = xmltodict.parse(f.read())
    name, act_type, date = extract_metadata_gpx(dct)
    if 'trk' in dct['gpx']:
        trkpts = dct['gpx']['trk']['trkseg']['trkpt']
        # Iterate through each trackpoint by index
        for trkpt in trkpts:
            list_of_trkpt_dicts.append(unpack_gpx_trkpt(trkpt))
    else:
        list_of_trkpt_dicts = []
    return name, act_type, date, pd.DataFrame(list_of_trkpt_dicts)


# ____________ Helper functions for parse_tcx() ____________

def extract_metadata_tcx(xmldict):
    act_type = xmldict['TrainingCenterDatabase']['Activities']['Activity']['@Sport']
    date = datetime.datetime.strptime(xmldict['TrainingCenterDatabase']['Activities']['Activity']['Id'], '%Y-%m-%dT%H:%M:%S.%fZ')
    if act_type == 'Biking':
        act_type = 'cycling'
    elif act_type == 'Running':
        act_type = 'running'
    name = '{} activity on {}'.format(act_type, date.strftime('%Y-%m-%d'))
    return name, act_type, date


def unpack_tcx_trkpt(trkpt):
    """
    Currently only formatted to accept TCX files where GPS has been turned off for activity recording, since I only need this format for processing rides data from the stationary bike
    """
    trackpoint = {}
    trackpoint['time'] = datetime.datetime.strptime(trkpt['Time'], '%Y-%m-%dT%H:%M:%S.%fZ')
    if 'HeartRateBpm' in trkpt:
        trackpoint['hr'] = int(trkpt['HeartRateBpm']['Value'])
    return trackpoint


def unpack_tcx(filepath):
    """
    Unpacks TCX XML file constructed by Garmin device (currently tested for Forerunner 230) containing a single lap.

    Returns tuple of name, activity type, activity date (as datetime object), and dataframe containing observational data for each trackpoint.
    """
    list_of_trkpt_dicts = []
    with open(filepath, 'r') as f:
        dct = xmltodict.parse(f.read())
    name, act_type, date = extract_metadata_tcx(dct)
    trkpts = dct['TrainingCenterDatabase']['Activities']['Activity']['Lap']['Track']['Trackpoint']
    # Iterate through each trackpoint by index
    for trkpt in trkpts:
        list_of_trkpt_dicts.append(unpack_tcx_trkpt(trkpt))
    return name, act_type, date, pd.DataFrame(list_of_trkpt_dicts)


# _____________________________________________________________

def parse_gpx(filepath,  zones=[113, 150, 168, 187]):
    """
    Returns tuple of name, activity_type, date, and dataframe of trackpoint data with engineered features and nulls filled with imputed values.
    """
    n, a, d, df = unpack_gpx(filepath)
    a, df = correct_activity_type(a, df)
    n, a, d, df = engineer_features(n, a, d, df, zones=zones)
    n, a, d, df = impute_nulls(n, a, d, df)
    return n, a, d, df


def parse_tcx(filepath, zones=[113, 150, 168, 187]):
    """
    Returns tuple of name, activity_type, date, and dataframe of trackpoint data with engineered features and nulls filled with imputed values.
    """
    n, a, d, df = unpack_tcx(filepath)
    a, df = correct_activity_type(a, df)
    n, a, d, df = engineer_features(n, a, d, df, zones=zones)
    n, a, d, df = impute_nulls(n, a, d, df)
    return n, a, d, df
