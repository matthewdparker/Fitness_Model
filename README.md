# Modeling Fitness using Wearables Data

[In Progress]

### Summary
This project is aimed at utilizing data from fitness wearables, including activity data and sleep & steps trackers to build a model predicting fitness, fatigue, and freshness on a given day for various activities.

### Model Features
- Cardio Score
    - Exponentially weighted average of all suffer scores across all activities from past X days (X TBD, likely 42 based on Strava)
- Activity Score
    - Exponentially weighted average of suffer scores from activity *i* from past X<sub>*i*</sub> days (X<sub>*i*</sub> TBD)
- Sleep Score
    - Exponentially weighted average of sleep from past M nights (M TBD, likely 2-3)
- Steps Score
    - Exponentially weighted average of steps from past N days (N TBD, likely 1-2)


### Model Outputs
- Activity Prediction (for each activity type)
    - Indicator of predicted performance for specific activity type on given day
- Fitness, Fatigue, Form values all available for viewing
    - Activity-specific, or overall (cardio)
