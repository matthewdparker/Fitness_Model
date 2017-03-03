# To Do

- Modify parse_xml to accommodate workouts where gps was off (e.g. treadmill/bike trainer)
    - In particular, trackseg_etree_to_trackpts_list function


- Modify parse_xml and/or calculate_stats to identify moving times (vs. stationary times). Once that is done:
    - Only increment time in zones/elevation/etc. when moving
    - Create avg_speed_2d, avg_speed_3d functions


- Consider exponentially down-weighting training loads from older activities (at different rates) for both fitness and fatigue calculations

- Consider structure of convoluting cardio and activity-specific values; is this even necessary?

- Write scripts to either pull sleep & steps data automatically from Garmin Connect, or to run against downloaded .csv of that data

- Engineer smoothing capabilities
    - Would this require creating whole new, smoothed GPX file?
