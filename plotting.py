import matplotlib.pyplot as plt
from class_defs import Activity
import seaborn as sns
import numpy as np
import datetime
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
from scipy.interpolate import spline
from calculate_stats import time_in_zones
from parse_xml import parse_gpx, parse_tcx
from utils import calculate_daily_training_loads, calculate_daily_fitness_fatigue_form


# _______________ Plotting Functions for Workout Data _______________

def plot_activity_HR(filepath, color_hr=False, show_zones=True):
    activity = Activity(filepath)
    hr_by_sec = [activity.heart_rates[0]]
    if activity.moving:
        hr = activity.heart_rates[activity.moving]
        time_deltas = activity.time_deltas[activity.moving]
    else:
        hr = activity.heart_rates
        time_deltas = activity.time_deltas

    for i in time_deltas.index[1:]:
        hr_by_sec += [hr[i]]*int(time_deltas[i])
    x = np.linspace(0, len(hr_by_sec)*1./60, len(hr_by_sec))
    hr_by_sec = np.array(hr_by_sec)

    if color_hr:
        cmap = ListedColormap(['b', 'limegreen', 'gold', 'darkorange', 'r'])
        norm = BoundaryNorm([0]+activity.zones+[250], cmap.N)
        points = np.array([x, hr_by_sec]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        points = np.array([x, hr_by_sec]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        lc = LineCollection(segments, cmap=cmap, norm=norm)
        lc.set_array(hr_by_sec)
        lc.set_linewidth(3)

        fig1 = plt.figure()
        plt.gca().add_collection(lc)
        plt.xlim(0, len(hr_by_sec)*1./60)

    else:
        plt.plot(x, hr_by_sec)

    if show_zones:
        [z1, z2, z3, z4] = activity.zones
        plt.axhline(y=z1, xmin=0, xmax=len(hr_by_sec)*1./60, linewidth=1, color = 'k', linestyle='dashed')
        plt.axhline(y=z2, xmin=0, xmax=len(hr_by_sec)*1./60, linewidth=1, color = 'k', linestyle='dashed')
        plt.axhline(y=z3, xmin=0, xmax=len(hr_by_sec)*1./60, linewidth=1, color = 'k', linestyle='dashed')
        plt.axhline(y=z4, xmin=0, xmax=len(hr_by_sec)*1./60, linewidth=1, color = 'k', linestyle='dashed')

    plt.show()


def plot_activity_elevation(filepath, plot_grade=False, savefig=False):
    """
    Note: This function could definitely benefit from smoothing
    """
    activity = Activity(filepath)
    elevations = list(activity.elevations[activity.moving])
    distances = [i/3.28084 for i in activity.distances_2d_ft[activity.moving]]
    cumulative_distances = [sum(distances[:i]) for i in range(len(distances))]
    xnew = np.linspace(0, cumulative_distances[-1], cumulative_distances[-1])
    smoothed_elevation = spline(cumulative_distances, elevations, xnew)

    if plot_grade:

        elevation_changes = [0]+[elevations[i] - elevations[i-1] for i in range(1, len(elevations))]
        grades = [elevation_changes[i]/distances[i]*100 for i in range(len(elevations))]

        xgradnew = np.linspace(0, cumulative_distances[-1], cumulative_distances[-1])
        smoothed_grades = spline(cumulative_distances, grades, xgradnew)

        plt.subplot(211)
        plt.plot(xnew*3.28084/5280, smoothed_elevation)
        plt.title('Elevation')

        plt.subplot(212)
        plt.plot(xgradnew*3.28084/5280, smoothed_grades)
        plt.title('Grade')
        plt.xlabel('Distance')

    else:
        plt.plot(xnew*3.28084/5280, smoothed_elevation)
        plt.title('Elevation')
    plt.tight_layout()

    if savefig:
        plt.savefig(filepath)
    else:
        plt.show()


def plot_time_in_zones(filepath, zones=[113, 150, 168, 187], Max_hr=195):
    if filepath[-3:] == 'gpx':
        n, a, d, data = parse_gpx(filepath, zones=zones)
    elif filepath[-3:] == 'tcx':
        n, a, d, data = parse_tcx(filepath, zones=zones)

    min_hr, max_hr = data.hr.min(), data.hr.max()
    zones = [min(min_hr, 90)]+zones+[max(max_hr, Max_hr)]

    time_at_different_heart_rates = []
    for heart_rate in range(int(min_hr), int(max_hr)+1):
        time_at_different_heart_rates.append(round(data[data.hr == heart_rate].time_delta.sum()*1./60, 2))

    fig, ax = plt.subplots()
    axes = [ax, ax.twinx()]
    for ax in axes:
        ax.grid(b=False)
    data.time_delta[0] = 1.0
    axes[0].hist(data.hr, bins=zones, weights=data.time_delta.apply(int)*1./60, alpha=0.35)
    axes[1].plot(range(int(min_hr), int(max_hr)+1), time_at_different_heart_rates, color='g')
    axes[0].set_ylabel('Minutes at Specific Heart Rates')
    axes[1].set_xlabel('Heart Rate (BPM)')
    axes[1].set_ylabel('Minutes in Zones')

    plt.title('Heart Rate Results for {} \n'.format(n), fontsize=14)
    plt.tight_layout()
    plt.show()


# _______________ Plotting Functions for Multi-Day Stats _______________

def plot_fitness_fatigue_form(athlete, fitness=True, fatigue=True, form=True, activity_type='cardio', n_weeks=-1):
    cardio_stats, cycling_stats, running_stats = calculate_daily_fitness_fatigue_form(athlete)
    if activity_type == 'cardio':
        stats = cardio_stats
    elif activity_type == 'cycling':
        stats = cycling_stats
    elif activity_type == 'running':
        stats = running_stats
    if n_weeks > 0:
        n_days = n_weeks*7
    else:
        n_days = len(stats[0])
    fitness = stats[0][-n_days:]
    fatigue = stats[1][-n_days:]
    form = stats[2][-n_days:]
    if fitness:
        plt.plot(fitness, label='Fitness')
    if fatigue:
        plt.plot(fatigue, label='Fatigue')
    if form:
        plt.plot(form, label='Form')
    plt.legend()
    plt.show()
