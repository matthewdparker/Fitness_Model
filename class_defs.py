import os
import glob
import datetime
import numpy as np
import pandas as pd
from operator import add, truediv
from parse_xml import parse_xml
from calculate_stats import time_in_zones, elevation, training_load, distance_2d, distance_3d, avg_speed_2d, avg_speed_3d, avg_cadence


class Activity(object):
    """
    Activities are never modified, everything about them is specified upon creation. Many attributes (e.g. temperatures, average speeds, etc.) are available which are not used in the current fitness model but felt like they were a waste to throw away.
    """
    def __init__(self, filepath, zones = [113, 150, 168, 187]):
        self.filepath = filepath
        self.name = None
        self.type = None
        self.date = None
        self.lats = None
        self.lons = None
        self.elevations = None
        self.heart_rates = None
        self.temps = None
        self.cadences = None
        self.avg_cadence = None
        self.zones = zones
        self.distances_2d_ft = None
        self.distances_3d_ft = None
        self.speeds_2d = None
        self.speeds_3d = None
        self.total_distance_2d = None
        self.total_distance_3d = None
        self.avg_speed_2d = None
        self.avg_speed_3d = None
        self.elevation_gain = None
        self.elevation_loss = None
        self.time_in_zone1 = None
        self.time_in_zone2 = None
        self.time_in_zone3 = None
        self.time_in_zone4 = None
        self.time_in_zone5 = None
        self.training_load = None
        self.init()

    def init(self):
        self.name, self.type, self.date, activity_info = parse_xml(self.filepath)

        if 'lat' in activity_info.columns.values:
            self.lats = activity_info.lat
            if 'lon' in activity_info.columns.values:
                self.lons = activity_info.lon
                self.distances_2d_ft = activity_info.distance_2d_ft
                self.distances_3d_ft = activity_info.distance_3d_ft
                self.speeds_2d = activity_info.speed_2d
                self.speeds_3d = activity_info.speed_3d
                self.total_distance_2d = distance_2d(activity_info)
                self.total_distance_3d = distance_3d(activity_info)
                self.avg_speed_2d = avg_speed_2d(activity_info)
                self.avg_speed_3d = avg_speed_3d(activity_info)

        if 'elevations' in activity_info.columns.values:
            self.elevations = activity_info.elevation
            gain, loss = elevation(activity_info)
            self.elevation_gain = gain
            self.elevation_loss = loss

        if 'hr' in activity_info.columns.values:
            self.heart_rates = activity_info.hr
            zones = time_in_zones(activity_info)
            self.time_in_zone1 = zones[0]
            self.time_in_zone2 = zones[1]
            self.time_in_zone3 = zones[2]
            self.time_in_zone4 = zones[3]
            self.time_in_zone5 = zones[4]
            self.training_load = training_load(activity_info)

        if 'air_temp' in activity_info.columns.values:
            self.temps = activity_info.air_temp

        if 'cadence' in activity_info.columns.values:
            self.cadences = activity_info.cadence
            self.avg_cadence = avg_cadence(activity_info)




class Activity_Stats(object):
    """
    Class contains same attributes as an Activity, but does not retain the data from the .gpx (e.g. individual TrackPoint data). Primary use is to be stored in activity_history attribute list of an Athlete.
    """
    def __init__(self, activity, zones = [113, 150, 168, 187]):
        self.name = None
        self.type = None
        self.date = None
        self.zones = zones
        self.distances_2d_ft = None
        self.distances_3d_ft = None
        self.speeds_2d = None
        self.speeds_3d = None
        self.total_distance_2d = None
        self.total_distance_3d = None
        self.avg_speed_2d = None
        self.avg_speed_3d = None
        self.elevation_gain = None
        self.elevation_loss = None
        self.time_in_zones = []
        self.init(activity)

    def init(self, activity):
        self.name = activity.name
        self.type = activity.type
        self.date = activity.date
        self.zones = activity.zones
        self.distances_2d_ft = activity.distances_2d_ft
        self.distances_3d_ft = activity.distances_3d_ft
        self.speeds_2d = activity.speeds_2d
        self.speeds_3d = activity.speeds_3d
        self.total_distance_2d = activity.total_distance_2d
        self.total_distance_3d = activity.total_distance_3d
        self.avg_speed_2d = activity.avg_speed_2d
        self.avg_speed_3d = activity.avg_speed_3d
        self.elevation_gain = activity.elevation_gain
        self.elevation_loss = activity.elevation_loss
        for zone in [activity.time_in_zone1, activity.time_in_zone2,
                     activity.time_in_zone3, activity.time_in_zone4,
                     activity.time_in_zone5]:
            self.time_in_zones.append(zone)
        self.training_load = activity.training_load




class Athlete(object):
    """
    Athletes are initialized with a max heart rate, and/or heart rate zones (top ends of ranges of first 4 of 5 zones)

    The most important methods are add_activity (which requires specifying filepath to gpx file), update_values (for updating fitness, fatigue, and form values when no workout was added in the last day or so), and update_sleep_values (which requires .csv of sleep data downloaded from Garmin Connect)
    """
    def __init__(self, max_hr=195, zones=None, print_fitness_vals=False):
        self.last_update = datetime.datetime.now()
        self.max_hr = max_hr
        if zones:
            self.zones = zones
        else:
            self.zones = [int(self.max_hr*0.59),
                          int(self.max_hr*0.78),
                          int(self.max_hr*0.87),
                          int(self.max_hr*0.97)]
        self.sleep_score = 100
        self.sleep_history = []
        self.activity_history = []
        self.cardio_fitness = 0
        self.cardio_fatigue = 0
        self.cardio_form = 0
        self.cycling_fitness = 0
        self.cycling_fatigue = 0
        self.cycling_form = 0
        self.running_fitness = 0
        self.running_fatigue = 0
        self.running_form = 0
        self.time_in_zones_7day = [0, 0, 0, 0, 0]
        self.time_in_zones_42day = [0, 0, 0, 0, 0]
        if print_fitness_vals:
            self.print_fitness_vals()

    def print_fitness_vals(self):
        print 'Sleep Score: {}'.format(self.sleep_score)
        print 'Cardio Fitness: {}'.format(self.cardio_fitness)
        print 'Cardio Fatigue: {}'.format(self.cardio_fatigue)
        print 'Cycling Fitness: {}'.format(self.cycling_fitness)
        print 'Cycling Fatigue: {}'.format(self.cycling_fatigue)
        print 'Running Fitness: {}'.format(self.running_fitness)
        print 'Running Fatigue: {}'.format(self.running_fatigue)

    def print_time_in_zones(self):
        x = map(int, map(truediv, self.time_in_zones_42day, [6]*5))
        y = map(int, self.time_in_zones_7day)
        print 'Average Weekly Minutes Zones Over Last 6 Weeks:\n\tZone 1: {}\n\tZone 2: {}\n\tZone 3: {}\n\tZone 4: {}\n\tZone 5: {}\n'.format(x[0], x[1], x[2], x[3], x[4])
        print 'Minutes in Zones Over Last 1 Week:\n\tZone 1: {}\n\tZone 2: {}\n\tZone 3: {}\n\tZone 4: {}\n\tZone 5: {}'.format(y[0], y[1], y[2], y[3], y[4])

    def add_all_from_folder(self, filepath, print_fitness_vals = True):
        self.add_activities_from_folder(filepath)
        for csv_file in glob.glob(os.path.join(filepath, '*.csv')):
            self.update_sleep_values(csv_file)
        if print_fitness_vals:
            self.print_fitness_vals()

    def add_activities_from_folder(self, filepath, print_fitness_vals=False):
        for gpx_file in glob.glob(os.path.join(filepath, '*.gpx')):
            self.add_activity(gpx_file)
        if print_fitness_vals:
            self.print_fitness_vals()

    def add_activity(self, filepath, print_fitness_vals=False):
        activity_full = Activity(filepath, self.zones)
        activity = Activity_Stats(activity_full)
        # Check to see if activity already exists by comparing dates (which include precision down to min/sec)
        new_activity = True
        for old_activity in self.activity_history:
            if old_activity.date == activity.date:
                new_activity = False
        if new_activity:
            self.activity_history.append(activity)
            # Sort oldest to newest
            # Minimizes shuffling if most added activities are more recent
            self.activity_history.sort(key = lambda x : x.date)
            self.update_fitness_values()
        else:
            print "Activity at {} is a duplicate of an existing activity".format(filepath)
        if print_fitness_vals:
            self.print_fitness_vals()

    def update_fitness_values(self):
        """
        This method is purely a helper for other updating methods. Updates fitness/fatigue/form values and time_in_zones_42day, time_in_zones_7day to match self.activity_history.
        """
        current_time = datetime.datetime.now()
        cardio_fitness_loads = []
        cardio_fatigue_loads = []
        cycling_fitness_loads = []
        cycling_fatigue_loads = []
        running_fitness_loads = []
        running_fatigue_loads = []
        time_in_zones_7day = [0, 0, 0, 0, 0]
        time_in_zones_42day = [0, 0, 0, 0, 0]
        for activity in self.activity_history:
            # If the activity date is less than 6 weeks ago, add to fitness_loads
            if (current_time - activity.date).total_seconds() < 3628800:
                cardio_fitness_loads.append(activity.training_load)
                time_in_zones_42day = map(add, time_in_zones_42day, activity.time_in_zones)
                if activity.type == 'cycling':
                    cycling_fitness_loads.append(activity.training_load)
                elif activity.type == 'running':
                    running_fitness_loads.append(activity.training_load)
                if ((current_time - activity.date).total_seconds() < 604800):
                    cardio_fatigue_loads.append(activity.training_load)
                    time_in_zones_7day = map(add, time_in_zones_7day, activity.time_in_zones)
                    if activity.type == 'cycling':
                        cycling_fatigue_loads.append(activity.training_load)
                    elif activity.type == 'running':
                        running_fatigue_loads.append(activity.training_load)

        self.cardio_fitness = int(sum(cardio_fitness_loads)*1./42)
        self.cardio_fatigue = int(sum(cardio_fatigue_loads)*1./7)
        self.cycling_fitness = int(sum(cycling_fitness_loads)*1./42)
        self.cycling_fatigue = int(sum(cycling_fatigue_loads)*1./7)
        self.running_fitness = int(sum(running_fitness_loads)*1./42)
        self.running_fatigue = int(sum(running_fatigue_loads)*1./7)
        self.time_in_zones_7day = time_in_zones_7day
        self.time_in_zones_42day = time_in_zones_42day

        # Iterate through and update all form values
        self.update_form_values()

        # Update last_update
        self.last_update = datetime.datetime.now()

    def update_form_values(self):
        self.cardio_form = self.cardio_fitness - self.cardio_form
        self.cycling_form = self.cycling_fitness - self.cycling_form
        self.running_form = self.running_fitness - self.running_form

    def update_sleep_values(self, filepath):
        """
        Updates sleep values according to .csv of sleep data downloaded from Garmin Connect saved at specified filepath
        """
        sleep_df = pd.read_csv(filepath, skiprows=[0, 1])
        self.sleep_history = list(sleep_df.iloc[:,1])
        mean_sleep = np.mean(self.sleep_history)
        self.sleep_score = round(100*(np.mean(self.sleep_history[-3:])/mean_sleep), 1)
        self.last_update = datetime.datetime.now()

    def update_hr_info(self, Max_hr=None, Zones=None):
        """
        Can specify either max_hr or zones, or both. If only one is provided, the other will be updated based on the specified value; e.g. if only max_hr is specified, zones will be updated as a percent of max_hr.
        """
        if Zones:
            self.zones = Zones
            if Max_hr:
                self.max_hr = Max_hr
            else:
                self.max_hr = int((Zones[0]*1./0.59 + Zones[1]*1./0.78 ++ Zones[2]*1./0.87 + Zones[4]*1./0.97)/4)

        elif Max_hr:
            self.max_hr = Max_hr
            if Zones == self.zones:
                self.zones = [int(Max_hr*0.59), int(Max_hr*0.78),
                              int(Max_hr*0.87), int(Max_hr*0.97)]
