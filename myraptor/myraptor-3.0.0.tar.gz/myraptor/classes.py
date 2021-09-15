import datetime
from datetime import datetime
import sys



class Timetable:
    """
    Class representing timetable, with routes, trips and stops.
    Attributes:
        routes: dictionary (contains all routes
                            key: raptor_id,
                            value: Route object)
        stops: dictionary (contains all stops,
                            key: stop_name,
                            value: Stop object)
        stop_names : list, contains all stops names

    """

    def __init__(self):
        self.routes = {}
        self.stops = {}
        self.stop_names = []

    def create_route(self, raptor_id):
        """
        Creates Route object
        Parameter: raptor_id (str)
        Returns: Route object
        """
        new_route = Route(raptor_id)
        self.routes[raptor_id] = new_route
        return new_route

    def get_route(self, raptor_id):
        """
        Recieves myraptor id (str), returns corresponding Route object
        Parameter: raptor_id (str)
        Returns: Route object
        """
        return self.routes[raptor_id]

    def create_trip(self, trip_id, raptor_id):
        """
        Creates Trip object
        Parameters: raptor_id (str)
                    trip_id (str)
        Returns: Trip object
        """
        route = self.get_route(raptor_id)
        new_trip = Trip(trip_id, route)
        route.trip_ids.append(new_trip)
        return new_trip

    def create_stop(self, stop_name):
        """
        Creates Stop object
        Parameter: stop_name (str)
        Returns: Stop object
        """
        new_stop = Stop(stop_name)
        self.stops[stop_name] = new_stop
        self.stop_names.append(stop_name)
        return new_stop


    def get_stop(self, stop_name):
        """
        Recieves stop name (str), returns corresponding Stop object
        Parameter: stop_name (str)
        Returns: Stop object
        """
        return self.stops[stop_name]


class Trip:
    """Class representing Trips. A trip is a sequence of two or more stops that
     occur during a specific time period.
    Attributes:
        trip_id
        number_of_stops
        route: route on which the trip operates
        stop_times_arr,stop_times_dep list, ordered sequence of arrival
         and departure times at all stops the trip contains
        (arrival_stop1,arrival_stop2,arrival_stop3,....)
    """
    def __init__(self, trip_id, route):
        self.trip_id = trip_id
        self.number_stops = 0
        self.route = route
        self.stop_times_arr = []
        self.stop_times_dep = []

    def get_stop_index(self, stop):
        """Returns index of given stop in the list route.stop_names
        operates
        Parameter: Stop object
        Returns: index (int)"""
        index = self.route.get_stop_index(stop)
        return index

    def get_arr_index(self, stop):
        """
        Returns index of arrival time to given stop in the list stop_times
        Parameter: Stop object
        Returns: index (int)
        """
        index = self.get_stop_index(stop)
        return index

    def get_arr(self, stop):
        """
        Returns  arrival time to given stop
        Parameter: Stop object
        Returns: arrival_time (datetime object)
        """
        return self.stop_times_arr[self.get_arr_index(stop)]

    def get_dep_index(self, stop):
        """
        Returns index of departure time from given stop in the list stop_times
        Parameter: Stop object
        Returns: index (int)
        """
        index = self.get_stop_index(stop)
        return index

    def get_dep(self, stop):
        """
        Returns  departure time from given stop
        Parameter: Stop object
        Returns: departure_time (datetime object)
        """
        dep = self.stop_times_dep[self.get_dep_index(stop)]
        return dep


class Route:
    """
    Class representing routes. A route is a group of trips that contains
    exactly same stops in same order.
    Attributes:
        raptor_id
        name : name of the line, eg. metro A, tram 22 etc.
        number_stops
        number_trips
        stop_names: list, ordered sequence of stop names of the route
        trip_ids: list, ordered list of trip ids operating the route
    """
    def __init__(self, raptor_id):
        self.raptor_id = raptor_id
        self.name = None
        self.number_stops = 0
        self.number_trips = 0
        self.stop_names = None
        self.trip_ids = []


    def get_stop_index(self, stop):
        """Returns index of given stop in the list stop_names
                operates
                Parameter: Stop object
                Returns: index (int)"""
        index = self.stop_names.index(stop.stop_name)
        return index

    def get_stop_sequence(self, stop):
        """Returns sequence of given stop in the list stop_names
                operates
            Parameter: Stop object
            Returns: sequence (int)"""
        sequence = self.get_stop_index(stop.stop_name) + 1
        return sequence

    def create_departure_list(self, stop):
        """Returns list of upward ordered departures from given stop of all
         trips belonging to the route
         Parameters: Stop object
         Returns departures (list)"""
        departures = []
        for trip in self.trip_ids:
            dep = trip.get_dep(stop)
            departures.append(dep)
        return departures



    def get_rest_stops(self, stop):
        """Returns ordered list of stop_names which follow after the given
        stop
        Parameter: Stop object
        Returns resto_stops (list)"""
        stop_index = self.stop_names.index(stop.stop_name)
        rest_stops = self.stop_names[(stop_index + 1):]
        return rest_stops

class Stop:
    """Class representing Stops
        Attributes:
            stop_name (str)
            routes (list, containes all routes serving the stop)
            best_arr (datetime object, set to max, changed if improved)
            dep_time (datetime object)
            marked (bool, marked = True if the stations best_arr was improved)
            self.previous_stop (Stop object)
            self.previous_line (str)
            self.previous_dep (datetime object)
            """
    def __init__(self, stop_name):
        self.stop_name = stop_name
        self.routes = []
        self.best_arr = sys.maxsize
        self.dep_time = None
        self.marked = False
        self.previous_stop = None
        self.previous_line = None
        self.previous_dep = None

    def get_path(self):
        """Returns path, how to get to the stop from the start_stop in form
        of list of tuples. Each tuple represents one stop from the path.The
        list contains exactly one start_stop tuple,any number of middle_stop
        tupples and exactly one target_stop tupple.
        Start_stop tuple contains start_stop_name, departure_time, line,
        middle_stops tuple contains
                        stop_name, arrival_time, departure_time, line
        target_stop tuple contains target_stop_name, arrival time."""
        path = [(self.stop_name,self.best_arr,None,None)]
        stop=self
        while stop.previous_stop:
            #(stop_name, arrival time, departure_time, line)
            path.append((stop.previous_stop.stop_name,
                         stop.previous_stop.best_arr,
                         stop.previous_dep,
                         stop.previous_line))
            stop = stop.previous_stop
        path.reverse()
        return path

    def improve_stop(self,arr,dep,current_stop,route):
        """ Executes changes to the Stop object attributes: improves arrival
        and departure times and sets previous stop and line"""
        self.best_arr = arr
        self.dep_time = dep
        self.previous_stop = current_stop
        self.previous_dep = dep
        self.previous_line = route.name
        self.marked = True
