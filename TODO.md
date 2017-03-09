# To Do

- Implement command-line functionality


- Start creating exciting graphs, charts, etc.
    - Evolution of stats over time
        - Fitness/Freshness/Fatigue
        - Weekly/Monthly Time in Zones
        - Percentages plot of activity profiles over time, like this one found at http://bit.ly/2mHAz60
    - Workout-specific plots
        - Plot fitness/freshness/fatigue (over time)
        - Plot HR, speed, elevation for a workout
        - Plot GPS data for workout
        - Plot time in zones
    - Marginal impact plots
        - Highlight the effect of workouts on fitness/fatigue/form, etc. plots
            - Allow selection of workouts, to see what it would look like without them
            - Allow user to create hypothetical workout, and see what fitness/freshness/fatigue would look like with them


- Consider moving calculate_stats functions into Activity class as methods
    - Consider also adding engineer_features and impute_nulls from parse_xml.py to Activity class as well


- Create functionality which allows for either/both profiling current fitness (e.g. distance, sprint, power, etc.), and setting a target fitness profile, by utilizing primarily time-in-zones data over time (both absolute, and proportional)


- Engineer smoothing capabilities
    - Would this require creating whole new, smoothed GPX file?


- Decide on long-term storage / reuse methods
    - Just pickle & unpickle Athlete object? Temporarily, yes
        - Long-term will shoot for app interface, with database of athletes & activities and credentialed login.


- Add functionality to allow user to input Strava login info and automatically pull activities from Strava API


- Look into whether it makes sense to define activity-specific zones; e.g. three hours cycling at 120 bpm is not identical (?) to three hours running at 140 bpm.


- Implement Sleep-Informed Scores (cardio fitness, cycling fatigue, etc.) which convolutes Sleep Score and other scores
    - Need to research a rigorous way to do this


- Consider models which convoluting cardio and activity-specific stats; is this even necessary?


- Make Zones attribute (and associated methods) more flexible, so users can put in their own number of zones [and respective upper limits of each zone]


- Consider starting to incorporate power analysis (including estimating power)
