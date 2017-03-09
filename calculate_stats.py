import numpy as np
import pandas as pd



def time_in_zones(df):
    times = []
    for i in range(1, 6):
        df_zone = df[df.zone == i]
        if 'moving' in df.columns.values:
            df_zone = df_zone[df_zone.moving == True]
        times.append(df_zone.time_delta.sum()/60)
    return times


def elevation(df):
    gain = df[df.elevation_change > 0].elevation_change.sum()
    loss = -df[df.elevation_change < 0].elevation_change.sum()
    return gain, loss


def training_load(df):
    times = time_in_zones(df)
    points_per_min = [0.2, 0.4, 0.75, 1.6667, 2.]
    return int(sum([times[i]*points_per_min[i] for i in range(5)]))


def distance_2d(df):
    return df.distance_2d_ft.sum()/5280


def distance_3d(df):
    return df.distance_3d_ft.sum()/5280


def moving_time(df):
    times = df[df.moving == True].time_delta
    moving_time = times.sum()
    return moving_time


def elapsed_time(df):
    elapsed_time = df.time_delta.sum()
    return elapsed_time


def avg_speed_2d(df):
    hrs = moving_time(df)*1./3600
    miles = distance_2d(df)
    return miles/hrs


def avg_speed_3d(df):
    hrs = moving_time(df)*1./3600
    miles = distance_3d(df)
    return miles/hrs


def avg_cadence(df):
    moving_df = df[df.moving == True]
    running_df = moving_df[moving_df.cadence>40]
    total_secs = running_df.time_delta.sum()
    total_cad = (running_df.time_delta*running_df.cadence).sum()
    avg_cad = total_cad*1. / total_secs
    return int(avg_cad)
