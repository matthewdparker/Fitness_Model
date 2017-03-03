import datetime
import numpy as np
import pandas as pd
from parse_xml import parse_xml, engineer_features
from calculate_stats import calculate_time_in_zones, calculate_elevation, calculate_training_load, calculate_distance_2d, calculate_distance_3d

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
        activity_info = engineer_features(activity_info)

        self.lats = activity_info.lat
        self.lons = activity_info.lon
        self.elevations = activity_info.elevation
        self.heart_rates = activity_info.hr
        # self.temps = activity_info.air_temp
        self.distances_2d_ft = activity_info.distance_2d_ft
        self.distances_3d_ft = activity_info.distance_3d_ft
        self.speeds_2d = activity_info.speed_2d
        self.speeds_3d = activity_info.speed_3d
        self.total_distance_2d = calculate_distance_2d(activity_info)
        self.total_distance_3d = calculate_distance_3d(activity_info)
        self.avg_speed_2d = None
        self.avg_speed_3d = None

        gain, loss = calculate_elevation(activity_info)
        self.elevation_gain = gain
        self.elevation_loss = loss

        zones = calculate_time_in_zones(activity_info)
        self.time_in_zone1 = zones[0]
        self.time_in_zone2 = zones[1]
        self.time_in_zone3 = zones[2]
        self.time_in_zone4 = zones[3]
        self.time_in_zone5 = zones[4]
        self.training_load = calculate_training_load(activity_info)



class Athlete(object):
    """
    Athletes are initialized with a max heart rate, and/or heart rate zones (top ends of ranges of first 4 of 5 zones)

    Most important methods are add_activity (which requires specifying filepath to gpx file), update_values (for updating fitness, fatigue, and form values when no workout was added in the last day or so), and update_sleep_values (which requires .csv of sleep data downloaded from Garmin Connect)
    """
    def __init__(self, max_hr=195, zones=None):
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

    def add_activity(self, filepath):
        activity = Activity(filepath, self.zones)
        activity_stats = {'date' : activity.date,
                          'type' : activity.type,
                          'training_load' : activity.training_load}
        self.activity_history.sort(key = lambda x : x['date'], reverse=True)
        self.activity_history.insert(0, activity_stats)
        self.update_fitness_values()

    def update_fitness_values(self):
        current_time = datetime.datetime.now()
        # Make sure activities are from the last 6 weeks (3,628,800 secs)
        for i in range(len(self.activity_history)):
            if (current_time - self.activity_history[i]['date']).total_seconds() > 3628800:
                del self.activity_history[i]

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
        mean_sleep = np.mean(sleep_vals)
        self.sleep_score = 100*(np.mean(sleep_vals[:3])/mean_sleep)
        self.last_update = datetime.datetime.now()
