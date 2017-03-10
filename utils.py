import datetime
import numpy as np
import cPickle as pickle


# Repository for random functions which are occasionally useful

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
        if activity.training_load != None:
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
        if activity.training_load:
            fatigue += activity.training_load*np.exp(-days_old*1./7)
    # Normalize by sum_{i=1}^{7}e^(-i/7)
    fatigue = int(round(fatigue/4.116, 0))
    return fatigue


def calc_norm_factor(n_days):
    nf = 0
    for i in range(n_days):
        nf += np.exp(-i*1./n_days)
    return round(nf, 3)


def calculate_daily_training_loads(athlete):
    # Find age of oldest activity
    current_date = datetime.datetime.now().date()
    activities = athlete.activity_history
    activities.sort(key = lambda x : x.date)
    oldest_date = activities[0].date.date()
    n_days = (current_date - oldest_date).days

    cardio_daily_tl = []
    cycling_daily_tl = []
    running_daily_tl = []
    # Iterate through activities list, append daily training load (or 0) to each activities list
    act_num = 0
    for age in range(n_days, -1, -1):
        # Initialize daily training loads are 0
        cardio_tl = 0
        cycling_tl = 0
        running_tl = 0
        try_next_act = True
        # Check if the next activity to be examined is the same age as our 'age' tracker. If so, update daily training loads respectively, and if not then continue.
        while try_next_act:
            if (current_date-activities[act_num].date.date()).days == age:
                if activities[act_num].training_load:
                    cardio_tl += activities[act_num].training_load
                    if activities[act_num].type == 'cycling':
                        cycling_tl += activities[act_num].training_load
                    elif activities[act_num].type == 'running':
                        running_tl += activities[act_num].training_load
                    # If all activities have been iterated through, exit. Otherwise, try the next activity in activities_list
                    if act_num == len(activities)-1:
                        try_next_act = False
                    else:
                        act_num += 1
            else:
                try_next_act = False
        cardio_daily_tl.append(cardio_tl)
        cycling_daily_tl.append(cycling_tl)
        running_daily_tl.append(running_tl)
    return cardio_daily_tl, cycling_daily_tl, running_daily_tl


def calculate_daily_fitness_fatigue_form(athlete):
    """
    Returns a tuple of (fitness, fatigue, form) cardio and each activity type. Currently, returns those values for cardio, cycling, and running.
    """
    cardio_loads, cycling_loads, running_loads = calculate_daily_training_loads(athlete)
    n_days = len(cardio_loads)

    # Create daily fitness lists for each activity type
    fitness_decay = [np.exp(-i*1./42) for i in range(n_days)]
    fitness_norm = sum(fitness_decay[:42])
    cardio_fitness_vals = [sum(np.multiply(cardio_loads[i::-1], fitness_decay[:i+1]))/fitness_norm for i in range(0, n_days)]
    cycling_fitness_vals = [sum(np.multiply(cycling_loads[i::-1], fitness_decay[:i+1]))/fitness_norm for i in range(0, n_days)]
    running_fitness_vals = [sum(np.multiply(running_loads[i::-1], fitness_decay[:i+1]))/fitness_norm for i in range(0, n_days)]

    # Create daily fatigue lists for each activity type
    cardio_adj_loads = [0]*6 + cardio_loads
    cycling_adj_loads = [0]*6 + cycling_loads
    running_adj_loads = [0]*6 + running_loads
    fatigue_weights = [np.exp(-x*1./7) for x in range(7)][::-1]
    fatigue_norm = sum(fatigue_weights)
    cardio_fatigue_vals = [sum(np.multiply(cardio_adj_loads[i:i+7], fatigue_weights))/fatigue_norm for i in range(n_days)]
    cycling_fatigue_vals = [sum(np.multiply(cycling_adj_loads[i:i+7], fatigue_weights))/fatigue_norm for i in range(n_days)]
    running_fatigue_vals = [sum(np.multiply(running_adj_loads[i:i+7], fatigue_weights))/fatigue_norm for i in range(n_days)]

    # Create daily form lists for each activity type
    cardio_form_vals = list(np.add(cardio_fitness_vals, [-i for i in cardio_fatigue_vals]))
    cycling_form_vals = list(np.add(cycling_fitness_vals, [-i for i in cycling_fatigue_vals]))
    running_form_vals = list(np.add(running_fitness_vals, [-i for i in running_fatigue_vals]))

    return [cardio_fitness_vals, cardio_fatigue_vals, cardio_form_vals], [cycling_fitness_vals, cycling_fatigue_vals, cycling_form_vals], [running_fitness_vals, running_fatigue_vals, running_form_vals]
