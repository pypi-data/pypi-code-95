from os import listdir
import re
from datetime import datetime
import os


def verifyDateFolder(dates_list):
    existed_folder_list = [x for x in dates_list if bool(re.match(r'(\d+\-\d+\-\d+)', x))]
    return existed_folder_list


def filterDates(dates_list, date_start, date_end):
    dates_to_check = []
    date_format = '%Y-%m-%d'

    date_start_entered = datetime.strptime(date_start, date_format)
    date_end_entered = datetime.strptime(date_end, date_format)

    dt_dates = [datetime.strptime(date, date_format) for date in dates_list]
    dt_dates_sorted = sorted(dt_dates)

    for date in dt_dates_sorted:
        if (date >= date_start_entered) and (date <= date_end_entered):
            dates_to_check.append(date.strftime(date_format))

    return dates_to_check


def validate_date(date_folder_path):
    date_exist = os.path.exists(date_folder_path)

    return date_exist


if __name__ == "__main__":
    area_folder_path = r"E:\data\wocket\Wockets-win32-x64\resources\app\src\srv\MICROT\aditya4_internal@timestudy_com\logs-watch"
    date_start = "2020-01-01"
    date_end = "2020-07-01"

    validated_date_list = validate_date(area_folder_path, date_start, date_end)
    print("Total number of valid date folders  :  {}".format(len(validated_date_list)))
    print(validated_date_list)
