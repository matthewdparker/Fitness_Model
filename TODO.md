# To Do

- Consider moving calculate_stats functions into Activity class as methods
    - Consider also adding engineer_features and impute_nulls from parse_xml.py to Activity class as well

- Modify parse_xml to accept activities without lat/long data (e.g. on treadmill or stationary bike/trainers when GPS was turned off)
    - Note: this will likely require processing TCX (rather than GPX) files


- Implement exponential down-weighting of stats (training loads, time in zones, etc.) from older activities (at different rates) for both fitness and fatigue calculations

- Implement exponential down-weighting of Sleep Score on both short (3-day) and long (up to 28-day) timescales

- Consider structure of convoluting cardio and activity-specific values; is this even necessary?


- Engineer smoothing capabilities
    - Would this require creating whole new, smoothed GPX file?


- Decide on long-term storage / reuse methods
    - Just pickle & unpickle Athlete object?


- Add functionality to allow user to input Strava login info and automatically pull activities from Strava API


- Look into whether it makes sense to define activity-specific zones; e.g. three hours cycling at 120 bpm is not identical (?) to three hours running at 140 bpm.


- Implement Sleep-Informed Scores (cardio fitness, cycling fatigue, etc.) which convolutes Sleep Score and other scores
