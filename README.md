# Modeling Fitness using Wearables Data

[In Progress]

### Summary
This project is aimed at utilizing data from fitness wearables, including activity data and sleep & steps trackers to build a model tracking fitness, fatigue, and freshness on a given day for various activities, and ideally learn to predict performance on a given day.

The model currently exclusively uses heart rate monitoring as a measure for effort, reflecting my personal usage of a HR monitor whenever I exercise, and the fact I don't have a cycling power meter/wattbike/etc. Other measures of effort/stress may be added in the future.

The model assigns training loads to each activity based on a points system derived from the amount of time spent in each HR zone, with different zones accumulating points at different rates.

### Model Outputs
- Cardio Fitness/Fatigue/Form Values
    - Currently just average of all training loads across all activities from past 6 weeks for Fitness, 1 week for Form (based on Strava's decisions).
- Activity-Specific F/F/F Values    
    - Currently just average of all training loads across activities of that specific type from past 6 weeks for Fitness, 1 week for Form (based on Strava's decisions).
- Sleep Score
    - Model calculates mean sleep over last 4 weeks as a baseline, then calculates sleep score to be average of most recent 3 nights as a percentage of baseline.
- Steps Score [coming soon]
    - Calculated similar to sleep score, but utilizing a 2-day rather than 3-day average

Note: I will be evaluating whether an exponentially down-weighted approach yields more realistic results for any of the above. Preliminary analysis suggests this would make sense.


### Requirements
- Activity data must be in GPX form from a Garmin device (for now, at least)
- Sleep and steps data must be in .csv form, downloaded from Garmin Connect, and must contain at least 3 days' worth of values
    - More is better; recommend downloading 28-day


### Sample Usage from Terminal
[coming soon]





### Sample Usage from Python Command Line

All data (.gpx files, .csv containing sleep data) contained in a single folder:
```python
>>> from class_defs import Athlete
>>> Matt = Athlete(print_fitness_vals=True)
Sleep Score: 0
Cardio Fitness: 0
Cardio Fatigue: 0
Cycling Fitness: 0
Cycling Fatigue: 0
Running Fitness: 0
Running Fatigue: 0

>>> Matt.add_all_from_folder('~/Desktop/Activity_Data/',
                             print_fitness_vals=True)
Sleep Score: 104.9
Cardio Fitness: 7
Cardio Fatigue: 29
Cycling Fitness: 6
Cycling Fatigue: 29
Running Fitness: 0
Running Fatigue: 0

```


Add all activity data (but not sleep data) contained in a single folder:
```python
>>> from class_defs import Athlete
>>> Matt = Athlete(print_fitness_vals=True)
Sleep Score: 0
Cardio Fitness: 0
Cardio Fatigue: 0
Cycling Fitness: 0
Cycling Fatigue: 0
Running Fitness: 0
Running Fatigue: 0

>>> Matt.add_activities_from_folder('~/Desktop/Activity_Data/')
Sleep Score: 0
Cardio Fitness: 7
Cardio Fatigue: 29
Cycling Fitness: 6
Cycling Fatigue: 29
Running Fitness: 0
Running Fatigue: 0
```


Check time in zones over last 7 days, 6 weeks:
```python
>>> from class_defs import Athlete
>>> Matt = Athlete()
>>> Matt.add_all_from_folder(print_fitness_vals=False)
>>> Matt.print_time_in_zones()
Minutes in Zones Over Last 6 Weeks:
	Zone 1: 3
	Zone 2: 224
	Zone 3: 252
	Zone 4: 27
	Zone 5:0

Minutes in Zones Over Last 1 Week:
	Zone 1: 0
	Zone 2: 56
	Zone 3: 60
	Zone 4: 17
	Zone 5:0
```
Other useful methods include:
- add_activity(filepath_to_gpx), to add individual activities
- update_sleep_values(filepath_to_csv), to overwrite sleep values
