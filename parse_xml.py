import pandas as pd
import numpy as np
import datetime
from xml.etree import ElementTree


def create_etree_from_file(filepath):
    with open(filepath, 'r') as f:
        xml_str=f.read().replace('\n', '')
    return ElementTree.fromstring(xml_str)


def trackseg_etree_to_trackpts_list(trackseg):
    """Convert etree tracksegment to list of dictionaries, each corresponding to a single trackpoint, containing keys/values for lat, lon, elevation, time, air_temp, and heart rate. Impute missing values as the mean of surrounding values.
    """
    trackpoints = []
    # try_air_temp = True
    # if not trackseg[0][2][0][0]:
    #     try_air_temp = False
    # try_hr = True
    # if not trackseg[0][2][0][1]:
    #     try_hr = False

    for i in range(len(trackseg)):
        trackpoint = {}
        trackpoint['lat'] = float(trackseg[i].attrib['lat'])
        trackpoint['lon'] = float(trackseg[i].attrib['lon'])
        try:
            trackpoint['elevation'] = float(trackseg[i][0].text)
        except:
            trackpoint['elevation'] = (float(trackseg[i-1][0].text)+float(trackseg[i+1][0].text))/2
        try:
            trackpoint['time'] = datetime.datetime.strptime(trackseg[i][1].text, '%Y-%m-%dT%H:%M:%S.%fZ')
        except:
            trackpoint['time'] = datetime.datetime.strptime(trackseg[i-1][1].text, '%Y-%m-%dT%H:%M:%S.%fZ') + (datetime.datetime.strptime(trackseg[i+1][1].text, '%Y-%m-%dT%H:%M:%S.%fZ') - datetime.datetime.strptime(trackseg[i-1][1].text, '%Y-%m-%dT%H:%M:%S.%fZ'))
        # if try_air_temp:
        #     try:
        #         trackpoint['air_temp'] = float(trackseg[i][2][0][0].text)
        #     except:
        #         trackpoint['air_temp'] = (float(trackseg[i-1][2][0][0].text)+float(trackseg[i+1][2][0][0].text))/2
        # if try_hr:
        try:
            trackseg[i][2][0][1]
            try:
                trackpoint['hr'] = int(trackseg[i][2][0][1].text)
            except:
                try:
                    trackpoint['hr'] = int((float(trackseg[i-1][2][0][1].text)+float(trackseg[i-1][2][0][1].text))/2)
                except:
                    trackpoint['hr'] = float(trackseg[i-1][2][0][1].text)
        except:
            try:
                trackpoint['hr'] = int(trackseg[i][2][0][0].text)
            except:
                try:
                    trackpoint['hr'] = int((float(trackseg[i-1][2][0][0].text)+float(trackseg[i-1][2][0][0].text))/2)
                except:
                    trackpoint['hr'] = float(trackseg[i-1][2][0][0].text)

        trackpoints.append(trackpoint)
    return trackpoints


def track_etree_to_track_dict(tree):
    '''Takes etree created from Garmin XML, parses out data for first track segment only'''
    d = {}
    d['name'] = tree[1][0].text
    d['type'] = tree[1][1].text
    d['date'] = datetime.datetime.strptime(tree[0][1].text[:10], '%Y-%m-%d')
    d['trackpoints'] = trackseg_etree_to_trackpts_list(tree[1][2])
    return d


def parse_xml_track_to_dict(filepath):
    tree = create_etree_from_file(filepath)
    return track_etree_to_track_dict(tree)


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


def extract_track_dict_info_to_df(track_dict):
    # Convert trackpoint data to dataframe
    track_info = pd.DataFrame(track_dict['trackpoints'])
    return track_info


def engineer_features(track_info, zones=[113, 150, 168, 187]):
    # 'time_delta' is elapsed time between successive points
    track_info['time_delta'] = (track_info.time - track_info.time.shift(1)).apply(lambda x : x.total_seconds())
    # 'elevation_change' is change in elevation between successive points
    track_info['elevation_change'] = track_info.elevation - track_info.elevation.shift(1)
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
    # 'zone' is heart rate zone during that point
    track_info['zone'] = track_info.hr.apply(calculate_zone)
    # calculate 2d distances between consecutive points
    track_info['distance_2d_ft'] = haversine_np(track_info.lon.shift(),
                     track_info.lat.shift(),
                     track_info.ix[1:, 'lon'],
                     track_info.ix[1:, 'lat'])
    # calculate 3d distances between consecutive points
    track_info['distance_3d_ft'] = np.sqrt(track_info.distance_2d_ft**2 +
                     track_info.elevation_change**2)
    track_info['speed_2d'] = (track_info.distance_2d_ft/5280)/(track_info.time_delta/3600)
    track_info['speed_3d'] =     track_info['speed_2d'] = (track_info.distance_3d_ft/5280)/(track_info.time_delta/3600)

    return track_info


def clean_df_to_only_moving_points(df):
    pass


def parse_xml(filepath):
    track = parse_xml_track_to_dict(filepath)
    df = extract_track_dict_info_to_df(track)
    df = engineer_features(df)
    return track['name'], track['type'], track['date'], df
