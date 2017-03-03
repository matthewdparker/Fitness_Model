import numpy as np
import pandas as pd

def calculate_time_in_zones(df):
    times = []
    for i in range(1, 6):
        times.append(df[df.zone == i].time_delta.sum()/60)
    return times


def calculate_elevation(df):
    gain = df[df.elevation_change > 0].elevation_change.sum()
    loss = -df[df.elevation_change < 0].elevation_change.sum()
    return gain, loss


def calculate_training_load(df):
    times = calculate_time_in_zones(df)
    points_per_min = [0.2, 0.4, 0.75, 1.6667, 2.]
    return int(sum([times[i]*points_per_min[i] for i in range(5)]))


def calculate_distance_2d(df):
    return df.distance_2d_ft.sum()/5280


def calculate_distance_3d(df):
    return df.distance_3d_ft.sum()/5280
