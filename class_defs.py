import os
import glob
import seaborn
import datetime
import numpy as np
import pandas as pd
import cPickle as pickle
import matplotlib.pyplot as plt
from operator import add, truediv
from scipy.interpolate import spline
from parse_xml import parse_gpx, parse_tcx
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
from utils import calc_fit_from_list, calc_fat_from_list, calc_norm_factor
from calculate_stats import time_in_zones, elevation, training_load, distance_2d, distance_3d, avg_speed_2d, avg_speed_3d, avg_cadence


class Activity(object):
    """
    Activities are never modified, all attributes are specified upon creation. Many attributes (e.g. temperatures, average speeds, etc.) are available which are not used in the current fitness model but felt like they were a waste to throw away.
    """
    def __init__(self, filepath, zones = [113, 150, 168, 187]):
        self.filepath = filepath
        self.filetype = filepath.split('.')[-1]
        self.name = None
        self.creator = None
        self.type = None
        self.date = None
        self.time_deltas = None
        self.moving = None
        self.lats = None
        self.lons = None
        self.elevations = None
        self.heart_rates = None
        self.heart_rate_zones = None
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
        if self.filetype == 'gpx':
            self.name, self.type, self.date, self.creator, activity_info = parse_gpx(self.filepath, zones=self.zones)
        elif self.filetype == 'tcx':
            self.name, self.type, self.date, self.creator, activity_info = parse_tcx(self.filepath, zones=self.zones)

        if 'time_delta' in activity_info.columns.values:
            self.time_deltas = activity_info.time_delta

        if 'lat' in activity_info.columns.values:
            self.lats = activity_info.lat
            if 'lon' in activity_info.columns.values:
                self.lons = activity_info.lon
                self.distances_2d_ft = activity_info.distance_2d_ft
                self.distances_3d_ft = activity_info.distance_3d_ft
                self.total_distance_2d = distance_2d(activity_info)
                self.total_distance_3d = distance_3d(activity_info)
                if 'time_delta' in activity_info.columns.values:
                    self.speeds_2d = activity_info.speed_2d
                    self.speeds_3d = activity_info.speed_3d
                    self.avg_speed_2d = avg_speed_2d(activity_info)
                    self.avg_speed_3d = avg_speed_3d(activity_info)
                    self.moving = activity_info.moving

        if 'elevation' in activity_info.columns.values:
            self.elevations = activity_info.elevation
            gain, loss = elevation(activity_info)
            self.elevation_gain = gain
            self.elevation_loss = loss

        if 'hr' in activity_info.columns.values:
            self.heart_rates = activity_info.hr
            self.heart_rate_zones = activity_info.zone
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


    # ___________ Plotting Methods ___________


    def plot(self, hr=True, elevation=True, grade=True, hr_hist=False, zones_hist=False, hr_and_zones_hist=False, mark_hr_zones=False):
        # Plots all of HR, Zones, HR & Zones overlaid, Elevation, and Grades which are set to True
        fig, axes = plt.subplots(hr+elevation+grade+hr_hist+zones_hist+hr_and_zones_hist, 1)
        axes[0].set_title(self.name, fontsize=14)

        if hr:
            self.plot_hr(axes[0], mark_hr_zones=mark_hr_zones)
            if not (elevation or grade):
                axes[0].set_xlabel('Distance', fontsize=12)
        if elevation:
            index = hr+elevation-1
            self.plot_elevation(axes[elevation], grade=grade)
            if not grade:
                axes[index].set_xlabel('Distance', fontsize=12)
        if grade:
            index = hr+elevation+grade-1
            self.plot_grade(axes[index])
            axes[index].set_xlabel('Distance', fontsize=12)
        if hr_hist:
            index = hr+elevation+grade+hr_hist-1
            self.plot_hr_hist(axes[index])
            if not (zones_hist or hr_and_zones_hist):
                axes[index].set_xlabel('Heart Rate (BPM)')
        if zones_hist:
            index = hr+elevation+grade+hr_hist+zones_hist-1
            self.plot_time_in_zones_hist(axes[index])
            if not hr_and_zones_hist:
                axes[index].set_xlabel('Heart Rate (BPM)')
        if hr_and_zones_hist:
            index = hr+elevation+grade+hr_hist+zones_hist+hr_and_zones_hist-1
            axes[index] = [axes[index], axes[index].twinx()]
            self.plot_hr_and_time_in_zones_hist(axes[index])
            axes[index][1].set_xlabel('Heart Rate (BPM)')

        for ax in axes[:-1]:
            labels = [item.get_text() for item in ax.get_xticklabels()]
            empty_string_labels = ['']*len(labels)
            ax.set_xticklabels(empty_string_labels)
        plt.show()


    def plot_hr(self, ax, mark_hr_zones=True):
        if self.moving[0] == None:
            result = self.plot_hr_by_time(ax, mark_hr_zones=mark_hr_zones)
        else:
            result = self.plot_hr_by_distance(ax, mark_hr_zones=mark_hr_zones)
        return result



    def plot_hr_by_distance(self, ax, mark_hr_zones=True):
        distances = [i/3.28084 for i in self.distances_2d_ft[self.moving]]
        cumulative_distances = [sum(distances[:i]) for i in range(len(distances))]
        xgrad = np.linspace(0, cumulative_distances[-1], cumulative_distances[-1])
        hr = self.heart_rates[self.moving]

        # Smooth heart rates by averaging
        hr = [np.mean(hr[0:2])] + [np.mean(hr[0:3])] + [np.mean(hr[i-2:i+3]) for i in range(2, len(hr)-2)] + [np.mean(hr[-3:])] + [np.mean(hr[-2:])]
        smoothed_HRs = spline(cumulative_distances, hr, xgrad)
        ax.set_ylabel('Heart Rate', fontsize=12)

        if mark_hr_zones:
            [z1, z2, z3, z4] = self.zones
            ax.axhline(y=z1, xmin=0, xmax=len(hr)*1./60, linewidth=1, color = 'k', linestyle='dashed')
            ax.axhline(y=z2, xmin=0, xmax=len(hr)*1./60, linewidth=1, color = 'k', linestyle='dashed')
            ax.axhline(y=z3, xmin=0, xmax=len(hr)*1./60, linewidth=1, color = 'k', linestyle='dashed')
            ax.axhline(y=z4, xmin=0, xmax=len(hr)*1./60, linewidth=1, color = 'k', linestyle='dashed')

        return ax.plot(xgrad*3.28084/5280, smoothed_HRs)



    def plot_hr_by_time(self, ax, mark_hr_zones=True):
        hr_by_sec = [self.heart_rates[0]]
        hr = self.heart_rates
        # Smooth heart rates by averaging
        hr = [np.mean(hr[0:2])] + [np.mean(hr[0:3])] + [np.mean(hr[i-2:i+3]) for i in range(2, len(hr)-2)] + [np.mean(hr[-3:])] + [np.mean(hr[-2:])]

        time_deltas = self.time_deltas

        for i in time_deltas.index[1:]:
            hr_by_sec += [hr[i]]*int(time_deltas[i])
        x = np.linspace(0, len(hr_by_sec)*1./60, len(hr_by_sec))
        hr_by_sec = np.array(hr_by_sec)
        ax.set_ylabel('Heart Rate', fontsize=12)

        if mark_hr_zones:
            [z1, z2, z3, z4] = self.zones
            plt.axhline(y=z1, xmin=0, xmax=len(hr_by_sec)*1./60, linewidth=1, color = 'k', linestyle='dashed')
            plt.axhline(y=z2, xmin=0, xmax=len(hr_by_sec)*1./60, linewidth=1, color = 'k', linestyle='dashed')
            plt.axhline(y=z3, xmin=0, xmax=len(hr_by_sec)*1./60, linewidth=1, color = 'k', linestyle='dashed')
            plt.axhline(y=z4, xmin=0, xmax=len(hr_by_sec)*1./60, linewidth=1, color = 'k', linestyle='dashed')

        return ax.plot(x, hr_by_sec)



    def plot_elevation(self, axis, grade=True):
        elevations = list(self.elevations[self.moving])
        distances = [i/3.28084 for i in self.distances_2d_ft[self.moving]]

        cumulative_distances = [sum(distances[:i]) for i in range(len(distances))]

        xgrad = np.linspace(0, cumulative_distances[-1], cumulative_distances[-1])

        smoothed_elevations = spline(cumulative_distances, elevations, xgrad)

        axis.set_ylabel('Elevation (ft)', fontsize=12)

        return axis.plot(xgrad*3.28084/5280, smoothed_elevations)


    def plot_grade(self, axes):
        elevations = list(self.elevations[self.moving])
        distances = [i/3.28084 for i in self.distances_2d_ft[self.moving]]

        cumulative_distances = [sum(distances[:i]) for i in range(len(distances))]

        elevation_changes = [0]+[elevations[i] - elevations[i-1] for i in range(1, len(elevations))]

        grades = [elevation_changes[i]/distances[i]*100 for i in range(len(elevations))]

        # Smooth out grades by eliminating outliers and averaging nearby values
        grades = [x if np.abs(x) < 22 else 0 for x in grades]
        grades = [np.mean(grades[0:2])] + [np.mean(grades[0:3])] + [np.mean(grades[i-2:i+3]) for i in range(2, len(grades)-2)] + [np.mean(grades[-3:])] + [np.mean(grades[-2:])]

        xgradnew = np.linspace(0, cumulative_distances[-1], cumulative_distances[-1])

        smoothed_grades = spline(cumulative_distances, grades, xgradnew)

        axes.set_ylabel('Grade')

        return axes.plot(xgradnew*3.28084/5280, smoothed_grades)



    def plot_hr_hist(self, axis):
        min_hr, max_hr = self.heart_rates.min(), self.heart_rates.max()
        zones = [min(min_hr, 90)]+self.zones+[max(max_hr, 195)]
        time_at_different_heart_rates = []
        for heart_rate in range(int(min_hr), int(max_hr)+1):
            time_at_different_heart_rates.append(round(self.time_deltas[self.heart_rates == heart_rate].sum()*1./60, 2))

        axis.set_ylabel('Min at HR')

        return axis.plot(range(int(min_hr), int(max_hr)+1), time_at_different_heart_rates, color='g')


    def plot_time_in_zones_hist(self, axis):
        min_hr, max_hr = self.heart_rates.min(), self.heart_rates.max()
        zones = [min(min_hr, 90)]+self.zones+[max(max_hr, 195)]
        time_deltas = pd.Series([1.0]).append(self.time_deltas[1:])

        axis.set_ylabel('Min in Zones')

        return axis.hist(self.heart_rates, bins=zones, weights=time_deltas.apply(int)*1./60, alpha=0.35)


    def plot_hr_and_time_in_zones_hist(self, axes):
        min_hr, max_hr = self.heart_rates.min(), self.heart_rates.max()
        zones = [min(min_hr, 90)]+self.zones+[max(max_hr, 195)]

        time_at_different_heart_rates = []
        for heart_rate in range(int(min_hr), int(max_hr)+1):
            time_at_different_heart_rates.append(round(self.time_deltas[self.heart_rates == heart_rate].sum()*1./60, 2))

        for ax in axes:
            ax.grid(b=False)
        time_deltas = pd.Series([1.0]).append(self.time_deltas[1:])
        axes[0].set_ylabel('Min in Zones')
        axes[1].set_ylabel('Min at HR')

        return axes[0].hist(self.heart_rates, bins=zones, weights=time_deltas.apply(int)*1./60, alpha=0.35), axes[1].plot(range(int(min_hr), int(max_hr)+1), time_at_different_heart_rates, color='g')


class Activity_Stats(object):
    """
    Class contains same attributes as an Activity, but does not retain the data from the .gpx (e.g. individual TrackPoint data). Primary use is to be stored in activity_history attribute list of an Athlete.
    """
    def __init__(self, activity, zones = [113, 150, 168, 187]):
        self.save_filepath = None
        self.last_saved_date = None
        self.name = None
        self.type = None
        self.creator = None
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
        self.training_load = 0
        self.init(activity)

    def init(self, activity):
        self.name = activity.name
        self.type = activity.type
        self.creator = activity.creator
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
        self.cardio_fitness_history = None
        self.cardio_fatigue_history = None
        self.cardio_form_history = None
        self.cycling_fitness_history = None
        self.cycling_fatigue_history = None
        self.cycling_form_history = None
        self.running_fitness_history = None
        self.running_fatigue_history = None
        self.running_form_history = None
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
        for tcx_file in glob.glob(os.path.join(filepath, '*.tcx')):
            self.add_activity(tcx_file)
        if print_fitness_vals:
            self.print_fitness_vals()

    def add_activity(self, filepath, print_fitness_vals=False):
        activity_full = Activity(filepath, zones=self.zones)
        activity = Activity_Stats(activity_full)
        if activity.date == None:
            if print_fitness_vals:
                self.print_fitness_vals()
            return
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
        cardio_fatigue_list = []
        cycling_fitness_list = []
        cycling_fatigue_list = []
        running_fitness_list = []
        running_fatigue_list = []
        time_in_zones_7day = [0, 0, 0, 0, 0]
        time_in_zones_42day = [0, 0, 0, 0, 0]
        for activity in self.activity_history:
            if activity.time_in_zones != [None, None, None, None, None]:
                time_in_zones_42day = map(add, time_in_zones_42day, activity.time_in_zones)
            if activity.type == 'cycling':
                cycling_fitness_list.append(activity)
            if activity.type == 'running':
                running_fitness_list.append(activity)
            if ((current_time - activity.date).total_seconds() < 604800):
                cardio_fatigue_list.append(activity)
                if activity.time_in_zones != [None, None, None, None, None]:
                    time_in_zones_7day = map(add, time_in_zones_7day, activity.time_in_zones)
                if activity.type == 'cycling':
                    cycling_fatigue_list.append(activity)
                elif activity.type == 'running':
                    running_fatigue_list.append(activity)
        # All activities contribute to cardio fitness
        self.cardio_fitness = calc_fit_from_list(self.activity_history)
        # All other stats are calculated from associated lists of activities
        self.cardio_fatigue = calc_fat_from_list(cardio_fatigue_list)
        self.cycling_fitness = calc_fit_from_list(cycling_fitness_list)
        self.cycling_fatigue = calc_fat_from_list(cycling_fatigue_list)
        self.running_fitness = calc_fit_from_list(running_fitness_list)
        self.running_fatigue = calc_fat_from_list(running_fatigue_list)
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
        n = len(self.sleep_history)
        # Calculate & normalize long-term exp. weighted sleep score
        total_sleep = 0
        for i in range(len(self.sleep_history)):
            total_sleep += self.sleep_history[i]*np.exp((i-n)*1./n)
        tot_norm_factor = calc_norm_factor(n)
        total_sleep = total_sleep/tot_norm_factor
        # Calculate & normalize short-term exp. weighted sleep score
        recent_sleep = 0
        for i in range(3):
            recent_sleep += self.sleep_history[-i]*np.exp(-i*1./3)
        rec_norm_factor = calc_norm_factor(3)
        recent_sleep = recent_sleep/rec_norm_factor
        # Update athlete attributes
        self.sleep_score = round(100*(recent_sleep/total_sleep), 1)
        self.last_update = datetime.datetime.now()

    def save(self):
        current_time = datetime.datetime.now()
        with open(self.filepath, 'w') as f:
            pickle.dump(self, f)
        self.last_saved_date = current_time

    def update_hr_info(self, Max_hr=None, Zones=None):
        """
        Can specify either max_hr or zones, or both. If only one is provided, the other will be updated based on the specified value; e.g. if only max_hr is specified, zones will be updated as a percent of max_hr.
        """
        if Zones:
            self.zones = Zones
            if Max_hr:
                self.max_hr = Max_hr
            else:
                self.max_hr = int((Zones[0]*1./0.59 + Zones[1]*1./0.78 + Zones[2]*1./0.87 + Zones[3]*1./0.97)/4)

        elif Max_hr:
            self.max_hr = Max_hr
            if Zones == self.zones:
                self.zones = [int(Max_hr*0.59), int(Max_hr*0.78),
                              int(Max_hr*0.87), int(Max_hr*0.97)]

    def save(self, filepath):
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)


    def update_historical_values(self):
        """
        Method updates attributes corresponding to historical daily fitness/fatigue/form for each activity type. It runs a bit slowly, so it's temporarily omitted from the update_fitness_values method
        """
        self.cardio_fitness_history, self.cardio_fatigue_history, self.cardio_form_history = self.calculate_daily_fitness_fatigue_form()
        self.cycling_fitness_history, self.cycling_fatigue_history, self.cycling_form_history = self.calculate_daily_fitness_fatigue_form(act_type='cycling')
        self.running_fitness_history, self.running_fatigue_history, self.running_form_history = self.calculate_daily_fitness_fatigue_form(act_type='running')


    def calculate_daily_training_loads(self, act_type):
        # Find age of oldest activity
        current_date = datetime.datetime.now().date()
        activities = self.activity_history
        activities.sort(key = lambda x : x.date)
        oldest_date = activities[0].date.date()
        n_days = (current_date - oldest_date).days
        training_loads = []
        # Iterate through activities list, append daily training load (or 0) to each activities list
        act_num = 0
        for age in range(n_days, -1, -1):
            # Initialize daily training loads are 0
            tl = 0
            try_next_act = True
            # Check if the next activity to be examined is the same age as our 'age' tracker. If so, update daily training loads respectively, and if not then continue
            while try_next_act:
                if (current_date-activities[act_num].date.date()).days == age:
                    if activities[act_num].training_load:
                        if act_type == activities[act_num].type:
                            tl += activities[act_num].training_load
                            # If all activities have been iterated through, exit. Otherwise, try the next activity
                            if act_num == len(activities)-1:
                                try_next_act = False
                            else:
                                act_num += 1
                        else:
                            try_next_act = False
                    else:
                        try_next_act = False
                else:
                    try_next_act = False
            training_loads.append(tl)
        return training_loads


    def calculate_daily_fitness_fatigue_form(self, act_type):
        """
        Returns a tuple of (fitness, fatigue, form) for a specific activity type. Currently works for activity types cardio, cycling, and running.
        """
        training_loads = self.calculate_daily_training_loads(act_type)
        import pdb; pdb.set_trace()
        n_days = len(training_loads)

        # Create exponentially decayed daily fitness values
        fitness_decay = [np.exp(-i*1./42) for i in range(n_days)]
        fitness_norm = sum(fitness_decay[:42])
        fitness_vals = [sum(np.multiply(training_loads[i::-1], fitness_decay[:i+1]))/fitness_norm for i in range(0, n_days)]

        # Create exponentially decayed daily fatigue values
        adjusted_loads = [0]*6 + training_loads
        fatigue_weights = [np.exp(-x*1./7) for x in range(7)][::-1]
        fatigue_norm = sum(fatigue_weights)
        fatigue_vals = [sum(np.multiply(adjusted_loads[i:i+7], fatigue_weights))/fatigue_norm for i in range(n_days)]

        # Create daily form values
        form_vals = list(np.add(fitness_vals, [-i for i in fatigue_vals]))

        return fitness_vals, fatigue_vals, form_vals


    def plot_fitness(self, incl_fitness=True, incl_fatigue=True, incl_form=True, activity_type='cardio', weeks=-1):
        if (activity_type == 'cardio') and self.cardio_fitness_history:
                fitness = self.cardio_fitness_history
                fatigue = self.cardio_fatigue_history,
                form = self.cardio_form_history
        elif (activity_type == 'cycling') and self.cycling_fitness_history:
                fitness = self.cycling_fitness_history
                fatigue = self.cycling_fatigue_history,
                form = self.cycling_form_history
        elif (activity_type == 'running') and self.running_fitness_history:
                fitness = self.running_fitness_history
                fatigue = self.running_fatigue_history,
                form = self.running_form_history
        else:
            fitness, fatigue, form = self.calculate_daily_fitness_fatigue_form(activity_type)
        if weeks > 0:
            days = weeks*7
        else:
            days = len(fitness)
        fitness, fatigue, form = fitness[-days:], fatigue[-days:], form[-days:]

        if incl_fitness:
            plt.plot(fitness, label='Fitness')
        if incl_fatigue:
            plt.plot(fatigue, label='Fatigue')
        if incl_form:
            plt.plot(form, label='Form')
        if incl_fitness:
            if incl_fatigue:
                if incl_form:
                    plt.title('Fitness, Fatigue, and Form over Trailing {} Weeks'.format(str(weeks)))
                else:
                    plt.title('Fitness and Fatigue over Trailing {} Weeks'.format(str(weeks)))
            elif form:
                plt.title('Fitness and Form over Trailing {} Weeks'.format(str(weeks)))
            else:
                plt.title('Fitness over Trailing {} Weeks'.format(str(weeks)))
        plt.legend()
        plt.show()
