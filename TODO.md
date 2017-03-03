# To Do

- Modify the way parse_xml accesses the data, to allow for more flexible data formats
    - Note: I might be completely just hacking away, instead of properly parsing the xml the way it was intended... the presence of the '{http://...}...' text in the tags, as below, concerns me.
    - E.g. create empty list to store general path along tree to HR data, and successively fill out (discover) each next step in the path, for each activity, using try...except's and recording successful attempts (e.g. tree[a][b]...[d].tag[-10:] == 'extensions', or tree[a][b]...[q].tag[-2:] == 'hr') in the list [a, b, c, ..., q]
        - Would require common tag structure across all devices; i.e. both forerunner and edge have tag structure:
            - '{http://www.topografix.com/GPX/1/1}gpx'
            - '{http://www.topografix.com/GPX/1/1}trk'
            - '{http://www.topografix.com/GPX/1/1}trkseg'
            - '{http://www.topografix.com/GPX/1/1}trkpt'
            - '{http://www.topografix.com/GPX/1/1}extensions'
            - '{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}TrackPointExtension'
            - '{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}hr'

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

- Decide on long-term storage / reuse methods
    - Just pickle & unpickle Athlete object?

- Create update_hr_info(max_hr=self.max_hr, zones=self.zones) method for Athlete object to allow updating of HR max/zones over time
