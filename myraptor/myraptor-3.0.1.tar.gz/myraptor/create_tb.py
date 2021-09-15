from io import BytesIO
import pandas as pd
import numpy as np
import datetime
from datetime import datetime
import sys
import pkgutil
from myraptor.classes import *
#from classes import *

source_data = 'data/data.csv'
source_data_stops = 'data/data_stops.csv'


def open_data_stops(source_data_stops):
    """Opens file containing dataset  concerning stops. Dataset was prepared
     in jupyter notebook data_raptor"""
    print ("Loading data, please wait....")
    data_open = pkgutil.get_data(__name__,source_data_stops)
    data_stops = pd.read_csv(BytesIO(data_open),
                             converters={'stop_routes_all': eval})
    return data_stops

def open_data(source_data):
    """Opens file containing dataset  concerning routes and trips. Dataset was
     prepared in jupyter notebook data_raptor"""
    data_open = pkgutil.get_data(__name__, source_data)
    data = pd.read_csv(BytesIO(data_open),
                       converters={'trip_arrival_times_seconds': eval,
                                   'trip_departure_times_seconds': eval,
                                   'trip_stop_names': eval})
    return data

def create_tb(data,data_stops):
    """Creates Timetable objects representing Prague public
    transport network (MHD). It contains Trip objects, Routes objects and
    Stop objects.
    Each row in prepaired dataset "data" contains data about one trip.
    Each row in prepaired dataset "data_stops" contains data about one stop."""
    print ("Creating timetable, please wait....")
    all_raptor_routes = data.route_raptor_id.unique()
    time1 = datetime.strptime('23:59:59','%H:%M:%S')
    tb = Timetable()
    #Creation of Trip objects (trip_stop_times list) and
    # Route objects (route_trips list)
    for routing in all_raptor_routes:
        #choose only data with the raptor_id
        data_route = data.loc[data["route_raptor_id"]==str(routing)]
        if routing == '':
            continue
        new_route = tb.create_route(routing)
        stops = data_route.iloc[0]["trip_stop_names"]
        name = data_route.iloc[0]["route_short_name"]
        new_route.stop_names = stops
        new_route.name = name
        for row in data_route.itertuples():
            if len(row.trip_departure_times_seconds) != len(
                    new_route.stop_names):
                break
            new_trip = tb.create_trip (row.trip_id,routing)
            new_trip.stop_times_arr = row.trip_arrival_times_seconds
            new_trip.stop_times_dep = row.trip_departure_times_seconds
            new_trip.number_stops +=1
            new_route.number_trips +=1
    #Creation of Stop objects (list stop_routes)
    for row in data_stops.itertuples():
        new_stop = tb.create_stop(row.stop_name)
        routes = row.stop_routes_all
        list_routes = []
        unique_routes = set(routes)
        for route in unique_routes:
            list_routes.append(route)
        new_stop.routes = list_routes
    return (tb)

