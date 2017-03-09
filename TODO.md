# To Do

- Implement command-line functionality


- Start creating exciting graphs, charts, etc.


- Consider moving calculate_stats functions into Activity class as methods
    - Consider also adding engineer_features and impute_nulls from parse_xml.py to Activity class as well


- Consider structure of convoluting cardio and activity-specific values; is this even necessary?


- Engineer smoothing capabilities
    - Would this require creating whole new, smoothed GPX file?


- Decide on long-term storage / reuse methods
    - Just pickle & unpickle Athlete object? Temporarily, yes
        - Long-term will shoot for app interface, with database of athletes & activities and credentialed login.


- Add functionality to allow user to input Strava login info and automatically pull activities from Strava API


- Look into whether it makes sense to define activity-specific zones; e.g. three hours cycling at 120 bpm is not identical (?) to three hours running at 140 bpm.


- Implement Sleep-Informed Scores (cardio fitness, cycling fatigue, etc.) which convolutes Sleep Score and other scores
    - Need a rigorous way to do this


- Make Zones attribute (and associated methods) more flexible, so users can put in their own number of zones [and respective upper limits of each zone]
