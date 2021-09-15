import pkgutil
from copy import deepcopy
from myraptor.helpers import *
#from helpers import *
from myraptor.classes import *
#from classes import *
from myraptor.raptor import raptor
#from raptor import raptor
from myraptor.create_tb import *


source_data = 'data/data.csv'
source_data_stops = 'data/data_stops.csv'

def main():
    timetable = create_tb(open_data(source_data),
                         open_data_stops(source_data_stops))
    while True:
        while True:
            tb = deepcopy(timetable)

            start_stop_name = load_start_stop(tb)
            target_stop_name = load_target_stop(tb)
            start_time_datetime = load_start_time()
            start_time = time_to_seconds(start_time_datetime)
            transfers = load_transfers()
            raptor(tb, start_stop_name, target_stop_name, start_time,
                   transfers)

            continue_or_no = load_yes_no()
            if continue_or_no == "y":
                continue
            elif continue_or_no == "n":
                print("Thank you for using myraptor!")
                break



if __name__ == '__main__':
    main()


