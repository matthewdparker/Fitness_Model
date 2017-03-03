from parse_xml import parse_xml, get_metadata
from calculate_stats import calculate_time_in_zones, calculate_elevation, calculate_training_load, calculate_distance_2d, calculate_distance_3d

class Activity(object):
    __init__(self, filepath, zones = [113, 150, 168, 187]):
        self.filepath = filepath
        self.name = None
        self.type = None
        self.date = None
        self.lats = None
        self.lons = None
        self.elevations = None
        self.heart_rates = None
        self.temps = None
        self.zones = zones
        self.distances_2d_ft = None
        self.distances_3d_ft = None
        self.speeds_2d = None
        self.speeds_3d = None
        self.total_distance_2d = None
        self.total_distance_3d = None
        self.avg_speed_2d = None
        self.avg_speed_3d = None
        self.elevation_gain = None
        self.elevation_loss = None
        self.time_in_zone1 = None
        self.time_in_zone2 = None
        self.time_in_zone3 = None
        self.time_in_zone4 = None
        self.time_in_zone5 = None
        self.training_load = None
        self.init()


    def init(self):
        self.name, self.type, self.date, activity_info = parse_xml(self.filepath)
        activity_info = engineer_features(activity_info)

        self.lats = activity_info.lat
        self.lons = activity_info.lon
        self.elevations = activity_info.elevation
        self.heart_rates = activity_info.hr
        self.air_temps = activity_info.air_temp
        self.distances_2d_ft = activity_info.distance_2d_ft
        self.distances_3d_ft = activity_info.distance_3d_ft
        self.speeds_2d = activity_info.speeds_2d
        self.speeds_3d = activity_info.speeds_3d
        self.total_distance_2d = calculate_distance_2d(activity_info)
        self.total_distance_3d = calculate_distance_3d(activity_info)
        self.avg_speed_2d = None
        self.avg_speed_3d = None

        gain, loss = calculate_elevation(activity_info)
        self.elevation_gain = gain
        self.elevation_loss = loss

        zones = calculate_time_in_zones(activity_info)
        self.time_in_zone1 = zones[0]
        self.time_in_zone2 = zones[1]
        self.time_in_zone3 = zones[2]
        self.time_in_zone4 = zones[3]
        self.time_in_zone5 = zones[4]
        self.training_load = calculate_training_load(activity_info)



class Athlete(object):
    """
    Athletes are initialized with a max heart rate, or heart rate zones (top end of first 4 of 5 zones).

    Most important methods are add_activity (which requires specifying filepath to gpx file), and update_values (for updating fitness, fatigue, and form values when no workout was added in the last day or so)
    """
    def __init__(self, max_hr=195, zones=None):
        self.max_hr = max_hr
        if zones:
            self.zones = zones
        else:
            self.zones = [int(self.max_hr*0.59),
                          int(self.max_hr*0.78),
                          int(self.max_hr*0.87),
                          int(self.max_hr*0.97)]
        self.activity_history = []
        self.cardio_fitness = 0
        self.cardio_fatigue = 0
        self.cardio_form = 0
        self.cycling_fitness = 0
        self.cycling_fatigue = 0
        self.cycling_form = 0
        self.running_fitness = 0
        self.running_fatigue = 0
        self.running_form = 0
        self.swimming_fitness = 0
        self.swimming_fatigue = 0
        self.swimming_form = 0


    def add_activity(self, filepath):
        activity = Activity(filepath, self.zones)
        activity_stats = {date : activity.date,
                          type : activity.type,
                          training_load : activity.training_load}
        self.activity_history.sort(key = lambda x : x['date'], reverse=True)
        self.activity_history.insert(0, activity_stats)
        self.update_values()


    def update_values(self):
        current_time = datetime.datetime.now()
        # Make sure activities are from the last 6 weeks (3,628,800 secs)
        for i in range(len(self.activity_history)):
            if (current_time - self.activity_history[i]['date']).total_seconds() > 3628800:
                del self.activity_history[i]

        # Iterate through and update each fitness & fatigue value
        self.clear_fit_and_fatigue_values()

        # Update cardio fitness & fatigue
        self.cario_fitness, self.cardio_fatigue = calculate_cardio_fit_and_fatigue()

        # Update fitness & fatigue values for each activity type
        self.cycling_fitness, self.cycling_fatigue = calculate_fit_and_fatigue('cycling')
        self.running_fitness, self.running_fatigue = calculate_fit_and_fatigue('running')
        self.swimming_fitness, self.swimming_fatigue = calculate_fit_and_fatigue('swimming')

        # Iterate through and update all form values
        self.update_form_values()


    def clear_fit_and_fatigue_values(self):
        self.cardio_fitness = 0
        self.cardio_fatigue = 0
        self.cycling_fitness = 0
        self.cycling_fatigue = 0
        self.running_fitness = 0
        self.running_fatigue = 0
        self.swimming_fitness = 0
        self.swimming_fatigue = 0


    def update_form_values(self):
        self.cardio_form = self.cardio_fitness - self.cardio_form
        self.cycling_form = self.cycling_fitness - self.cycling_form
        self.running_form = self.running_fitness - self.running_form
        self.swimming_form = self.swimming_fitness - self.swimming_form


    def calculate_cardio_fit_and_fatigue(self):
        fitness_loads = []
        fatigue_loads = []
        for activity in self.activity_history:
            fitness_loads.append(activity['training_load'])
            if ((current_time - activity['date']).total_seconds() < 604800):
                fatigue_loads.append(activity['training_load'])
        return int(sum(fitness_loads)*1./42), int(sum(fatigue_loads)*1./7)


    def calculate_fit_and_fatigue(self, activity_type):
        fitness_loads = []
        fatigue_loads = []
        for activity in self.activity_history:
            if activity['type'] == activity_type:
                fitness_loads.append(activity['training_load'])
                if ((current_time - activity['date']).total_seconds() < 604800):
                    fatigue_loads.append(activity['training_load'])
        return int(sum(fitness_loads)*1./42), int(sum(fatigue_loads)*1./7)
