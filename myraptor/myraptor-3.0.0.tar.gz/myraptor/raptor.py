from myraptor.helpers import *
#from helpers import *

def raptor(tb,start_stop_name,target_stop_name,start_time,max_transfers):
    """
    Function representing the myraptor algorithm
    Parameters: tb (Timetable object)
        start_stop_name (str)
        target_stop_name (str)
        start_time (datetime object)
        max_transfers (int)
    Returns :Fastest path from the start_stop to the target_stop (tuple (path,
    start_stop, target_stop))

    """
    #Creation of stop objects for the provided stop arguments
    start_stop = tb.get_stop(start_stop_name)
    target_stop = tb.get_stop(target_stop_name)

    #RAPTOR ALGORITHM
    # 1) Initialization : Update of start_station attribute best arrival time
    #                     Building Queue of updated stops

    start_stop.best_arr = start_time
    stop_queue = [start_stop]
    current_time = start_time
    # 2) First loop: represents rounds in the algorithm, while each round
    #                computes the fastest way of getting to every stop with
    #                at most k-1 transfers
    for transfer in range (max_transfers+1):
        stop_queue_previous = stop_queue
        while stop_queue_previous:
    # 3) First part of round: sets the current time to the best arrival time
    #    from the previous round
            stop_queue = []
            current_stop = stop_queue_previous.pop()
            current_time = current_stop.best_arr
            route_queue = [tb.get_route(route) for route in current_stop.routes]
    # 4) Second part of the round: processing of the routes
            while route_queue:
                route = route_queue.pop()

                #selection of data departure data concerning only current stop
                dep_current_stop = route.create_departure_list(current_stop)
                #selection of best departure time from current stop
                if dep_current_stop == []:
                    continue
                best_time =binary_search(dep_current_stop,current_time)
                dep = best_time[0]
                dep_index = best_time[1]
                if dep == None:
                    continue
                # selection of trip with best departure time
                current_trip = route.trip_ids[dep_index]
                # decision if the arrival time to the stop was improved
                for stop_name in route.get_rest_stops(current_stop):
                    stop = tb.get_stop(stop_name)
                    arr = current_trip.get_arr(stop)
                    if arr < stop.best_arr:
                        stop.improve_stop( arr, dep, current_stop, route)
                        if stop in stop_queue:
                            continue
                        stop_queue.append(stop)


    if target_stop.marked == False:
        print ("It is not possible to find the connection, try more"
               " transfers!")
        return None
    return (path_to_str(target_stop.get_path(),start_stop,target_stop))