# High-Level Structure of the Model

### Data Inputs
- Sleep (Daily)
- Steps (Daily)
- Activities (Workouts)
    - Distance
    - Time (Moving Time)
    - Elevation
    - Heart Rate
        - Time in Zones: Z1 - Z5
- HR Zones or Max HR or Age
    - Needed to determine zones


### Basic Constructs
- Suffer Score
    - av + bw + cx + dy + ez
        - a = 12/hr
        - b = 24/hr
        - c = 45/hr
        - d = 100/hr
        - e = 120/hr
        - v = Time in Zone 1 (in hrs)
        - ...
        - z = Time in Zone 5 (in hrs)
- Fitness*
    - Exponentially weighted average of stress (suffer scores) from past 7 days
- Fatigue*
    - Exponentially weighted average of stress (suffer scores) from past 42 days
- Form*
    - Fitness - Fatigue

*Can be activity-specific, or overall (cardio)


### Classes
- Athlete
    - Attributes:
        - HR_Zones
            - Ranges for Zones 1 - 5
        - Activity_History
            - Array of activity objects from past 42 days, for each specific activity type
        - Sleep_History
            - Array of sleep values from past M days
        - Step_History
            - Array of steps values from past N days
        - Max_HR (optional)
        - Age (optional)
    - Methods:
        - Need methods for calculating:
            - Cardio, Activity Scores
            - Sleep Score
            - Steps Score
        - Need methods for:
            - Adding activities of each type
            - Updating sleep, steps values
            - Predicting & outputting
- Activity
    - Attributes:
        - Activity type
        - Time in Zones
        - Time (timestamp)
        - Possibly: elevation, distance, time


### Model Features
- Cardio Score
    - Exponentially weighted average of all suffer scores across all activities from past 42 days
- Activity Score
    - Exponentially weighted average of suffer scores from that specific activity from past X days (X TBD)
- Sleep Score
    - Exponentially weighted average of sleep from past M nights (M TBD, likely 2-3)
- Steps Score
    - Exponentially weighted average of steps from past N days (N TBD, likely 1-2)


### Model Outputs
- Activity Prediction (for each activity type)
    - Indicator of predicted performance for specific activity type on given day
- Fitness, Fatigue, Form values all available for viewing
    - Activity-specific, or overall (cardio)
