import datetime
import numpy as np
import pandas as pd
import os
import glob
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



class Athlete(object):
    """
    Athletes are initialized with a max heart rate, and/or heart rate zones (top ends of ranges of first 4 of 5 zones)

    Most important methods are add_activity (which requires specifying filepath to gpx file), update_values (for updating fitness, fatigue, and form values when no workout was added in the last day or so), and update_sleep_values (which requires .csv of sleep data downloaded from Garmin Connect)
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
        self.sleep_score = 0
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
        self.swimming_fitness = 0
        self.swimming_fatigue = 0
        self.swimming_form = 0
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

    def add_all_from_folder(self, filepath):
        self.add_activities_from_folder(filepath)
        for csv_file in glob.glob(os.path.join(filepath, '*.csv')):
            self.update_sleep_values(csv_file)
        self.print_fitness_vals()

    def add_activity(self, filepath, print_fitness_vals=False):
        activity = Activity(filepath, self.zones)
        activity_stats = {'date' : activity.date,
                          'type' : activity.type,
                          'training_load' : activity.training_load}
        self.activity_history.sort(key = lambda x : x['date'], reverse=True)
        self.activity_history.insert(0, activity_stats)
        self.update_fitness_values()
        if print_fitness_vals:
            self.print_fitness_vals()

    def add_activities_from_folder(self, filepath, print_fitness_vals=False):
        for gpx_file in glob.glob(os.path.join(filepath, '*.gpx')):
            self.add_activity(gpx_file)
        if print_fitness_vals:
            self.print_fitness_vals()


    def update_fitness_values(self):
        """
        This method is purely a helper for other updating methods
        """
        current_time = datetime.datetime.now()
        new_activity_history = []
        # Make sure activities are from the last 6 weeks (3,628,800 secs)
        for i in range(len(self.activity_history)):
            if (current_time - self.activity_history[i]['date']).total_seconds() < 3628800:
                new_activity_history.append(self.activity_history[i])

        self.activity_history = new_activity_history

        # Iterate through and update each fitness & fatigue value
        self.clear_fit_and_fatigue_values()

        # Update cardio fitness & fatigue
        self.cardio_fitness, self.cardio_fatigue = self.calculate_cardio_fit_and_fatigue()

        # Update fitness & fatigue values for each activity type
        self.cycling_fitness, self.cycling_fatigue = self.calculate_fit_and_fatigue('cycling')
        self.running_fitness, self.running_fatigue = self.calculate_fit_and_fatigue('running')
        self.swimming_fitness, self.swimming_fatigue = self.calculate_fit_and_fatigue('swimming')

        # Iterate through and update all form values
        self.update_form_values()

        # Update last_update
        self.last_update = datetime.datetime.now()

    def clear_fit_and_fatigue_values(self):
        self.cardio_fitness = 0
        self.cardio_fatigue = 0
        self.cycling_fitness = 0
        self.cycling_fatigue = 0
        self.running_fitness = 0
        self.running_fatigue = 0
        self.swimming_fitness = 0
        self.swimming_fatigue = 0

    def update_form_values(self):
        self.cardio_form = self.cardio_fitness - self.cardio_form
        self.cycling_form = self.cycling_fitness - self.cycling_form
        self.running_form = self.running_fitness - self.running_form
        self.swimming_form = self.swimming_fitness - self.swimming_form

    def calculate_cardio_fit_and_fatigue(self):
        current_time = datetime.datetime.now()
        fitness_loads = []
        fatigue_loads = []
        for activity in self.activity_history:
            fitness_loads.append(activity['training_load'])
            if ((current_time - activity['date']).total_seconds() < 604800):
                fatigue_loads.append(activity['training_load'])
        return int(sum(fitness_loads)*1./42), int(sum(fatigue_loads)*1./7)

    def calculate_fit_and_fatigue(self, activity_type):
        current_time = datetime.datetime.now()
        fitness_loads = []
        fatigue_loads = []
        for activity in self.activity_history:
            if activity['type'] == activity_type:
                fitness_loads.append(activity['training_load'])
                if ((current_time - activity['date']).total_seconds() < 604800):
                    fatigue_loads.append(activity['training_load'])
        return int(sum(fitness_loads)*1./42), int(sum(fatigue_loads)*1./7)

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
