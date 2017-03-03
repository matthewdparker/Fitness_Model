# To Do

- Consider moving calculate_stats functions into Activity class as methods

- Modify parse_xml to accept activities without lat/long data (e.g. on treadmill or stationary bike/trainers when GPS was turned off)
    - Note: this will likely require processing TCX (rather than GPX) files


- Consider exponentially down-weighting training loads from older activities (at different rates) for both fitness and fatigue calculations

- Consider structure of convoluting cardio and activity-specific values; is this even necessary?


- Engineer smoothing capabilities
    - Would this require creating whole new, smoothed GPX file?


- Decide on long-term storage / reuse methods
    - Just pickle & unpickle Athlete object?


- Add functionality to allow user to input Strava login info and automatically pull activities from Strava API
