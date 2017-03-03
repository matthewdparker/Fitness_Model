# Modeling Fitness using Wearables Data

[In Progress]

### Summary
This project is aimed at utilizing data from fitness wearables, including activity data and sleep & steps trackers to build a model tracking fitness, fatigue, and freshness on a given day for various activities, and ideally learn to predict performance on a given day.

The model currently exclusively uses heart rate monitoring as a measure for effort, reflecting my personal usage of a HR monitor whenever I exercise, and the fact I don't have a cycling power meter/wattbike/etc. Other measures of effort/stress may be added in the future.

The model assigns training loads to each activity based on the amount of time spent in each HR zone, with different zones accumulating points at different rates.

### Model Outputs
- Cardio Fitness/Fatigue/Form Values
    - Currently just average of all training loads across all activities from past 6 weeks for Fitness, 1 week for Form (based on Strava's decisions).
- Activity-Specific F/F/F Values    
    - Currently just average of all training loads across activities of that specific type from past 6 weeks for Fitness, 1 week for Form (based on Strava's decisions).
- Sleep Score
    - Model calculates mean sleep over last 4 weeks as a baseline, then calculates sleep score to be average of most recent 3 nights as a percentage of baseline.
- Steps Score
    - Calculated similar to sleep score, but utilizing a 2-day rather than 3-day average
- I will be evaluating whether an exponentially down-weighted approach yields more realistic results for any of the above.


### Requirements
- Activity data must be in GPX form from a Garmin device (for now, at least)
- Sleep and steps data must be in .csv form, downloaded from Garmin Connect, and must contain at least 3 days' worth of values
    - More is better; recommend downloading 28-day
