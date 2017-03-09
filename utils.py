import datetime
import numpy as np
import cPickle as pickle

def load_saved_athlete(filepath):
    with open(filepath, 'rb') as f:
        athlete = pickle.load(f)
    return athlete

def calc_fit_from_list(activity_list):
    current_time = datetime.datetime.now()
    fitness = 0
    loads_and_ages = []
    for activity in activity_list:
        days_old = int((current_time-activity.date).total_seconds()*1/86400)
        fitness += activity.training_load*np.exp(-days_old*1./42)
    # Normalize by sum_{i=1}^{42}e^(-i/42)
    fitness = int(round(fitness/26.234, 0))
    return fitness

def calc_fat_from_list(activity_list):
    current_time = datetime.datetime.now()
    fatigue = 0
    loads_and_ages = []
    for activity in activity_list:
        days_old = int((current_time-activity.date).total_seconds()*1/86400)
        fatigue += activity.training_load*np.exp(-days_old*1./7)
    # Normalize by sum_{i=1}^{7}e^(-i/7)
    fatigue = int(round(fatigue/4.116, 0))
    return fatigue

def calc_norm_factor(n_days):
    nf = 0
    for i in range(n_days):
        nf += np.exp(-i*1./n_days)
    return round(nf, 3)
