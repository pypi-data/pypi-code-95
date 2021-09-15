import datetime as dt
from datetime import datetime


def binary_search(dep_times_list, start_time):
    """
    Function representing the binary search algorithm, from a list of ordered
    values (departure times) chooses value equal or closest (higher) to given
    parameter
    Parameters
    ----------
    dep_times_list: list of ordered datetime objects
    start_time: datetime object

    Returns: tuple of selected departure time and index of the time
    -------

    """
    #if start time earlier than all departure times, the first departure time
    #is chosen
    if (start_time <= dep_times_list[0]):
        return (dep_times_list[0], 0)
    #if start time is after all departure times, no connection is available
    #within this route, the best time is set to None
    if start_time > dep_times_list[len(dep_times_list) - 1]:
        return None,None
    left_index = 0
    right_index = len(dep_times_list) - 1

    while left_index <=right_index:
        if left_index == right_index:
            return (dep_times_list[left_index], left_index)
        middle_index = (left_index + right_index) // 2
        middle_time = dep_times_list[middle_index]
        if start_time > middle_time:
           left_index = middle_index + 1
        elif start_time < middle_time:
           right_index = middle_index
        else:
            return (dep_times_list[middle_index], middle_index)
    return (None, None)

def path_to_str(path, start_stop, target_stop):
    """ Prints the path from the start_stop to the target_stop in
     readable format"""
    for station in path:
        if station[0] == start_stop.stop_name:
            stop_name = station[0]
            departure_time = time_to_hhmmss(station[2])
            line = station[3]
            path_str = (
                f"stop: {stop_name},  "
                f"departure time: {departure_time},  "
                f"take line: {line}  "
            )
        elif station[0] == target_stop.stop_name:
            stop_name = station[0]
            arrival_time = time_to_hhmmss(station[1])
            path_str = (
                f"stop: {stop_name},  "
                f"arrival time: {arrival_time}  "
            )
        else:
            stop_name = station[0]
            arrival_time = time_to_hhmmss(station[1])
            departure_time = time_to_hhmmss(station[2])
            line = station[3]
            path_str = (
                f"stop: {stop_name},  "
                f"arrival time: {arrival_time},  "
                f"departure time: {departure_time},  "
                f"change to line: {line}  "
            )
        print(path_str)


def time_to_hhmmss(time):
    """Transfers time in form of total seconds to timedelta object in form
    of HH:MM:SS"""
    return str(dt.timedelta(seconds=time))

def time_to_str(time):
    """Receives timedelta object and transforms it to string
     in form HH:MM:SS"""
    return time.strftime("%H:%M:%S")



def load_start_stop (tb):
    """Asks the user to type start_stop. start stop must be in the list
        tb.stop_names. If not, the list of tb.stop_names is printed """
    while True:
        start_stop_name = input("Please enter start station: ")
        if start_stop_name in tb.stop_names:
            return start_stop_name
        else:
            print ("Not valid name of the station, please start again")
            print (sorted(tb.stop_names))


def load_target_stop (tb):
    """Asks the user to type target_stop. start stop must be in the list
        tb.stop_names. If not, the list of tb.stop_names is printed """
    while True:
        target_stop_name = input("Please enter target station: ")
        if target_stop_name in tb.stop_names:
            return target_stop_name
        else:
            print ("Not valid name of the station, please start again")
            print (sorted(tb.stop_names))



def load_start_time ():
    """Asks the user to type start_time in form HH:MM:SS """
    while True:
        start_time = input(
            "Please enter start time in form HH:MM:SS   :   ")
        try:
            time = datetime.strptime(start_time, '%H:%M:%S')
            return time
        except UnicodeDecodeError:
            start_time.encode("latin-1", "ignore")
            print (start_time)
            time = datetime.strptime(start_time, '%H:%M:%S')
        except:
            print ("Not valid format of time")


def time_to_seconds(time):
    """transfers datetime object HH:MM:SS and transfers it to seconds (float)"""
    time_zero = datetime.strptime('00:00:00', '%H:%M:%S')
    time_total = time - time_zero
    time_total = time_total.total_seconds()
    return time_total

def load_transfers ():
    """Asks the user to type maximum number of transfers allowed"""
    #TODO: check if the number is right
    while True:
        transfers = input("Please enter maximum allowed transfers in form of"
                          " number in range (0,10): ")
        try:
            return int(transfers)
        except UnicodeDecodeError:
            print("unicode")
            transfers.encode("latin-1", "ignore")
            return(int(transfers))
        except ValueError:
            print ("This is not a number")

def load_yes_no ():
    """Asks the user if he wants to find another connection, answer must
    be in form of str 'y' or 'n'"""
    while True:
        answer =input("Do you want to find another connection? y/n: ")
        if answer == "y":
            return answer
        elif answer[0] == "n":
            return answer
        else:
            print ("Please write y or n!")



