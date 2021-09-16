from datetime import datetime, timedelta
import pandas as pd
import numpy as np

nat = np.datetime64('NaT')


def parse_time_offset(time_offset):
    sign_str = time_offset.strip('GMT')[0]
    if sign_str == "-":
        sign = -1
    elif sign_str == "+":
        sign = 1
    else:
        sigh = 0

    time_offset_int = int(time_offset.strip('GMT')[1:3])
    time_delta = timedelta(hours=time_offset_int)

    return time_delta, sign


def get_time_offset(time_offset):
    time_delta = timedelta(hours=0)
    sign = 0

    time_delta, sign = parse_time_offset(time_offset)

    return time_delta, sign


def convert_timestamp_int_list_to_readable_time(timestamp_int_list, time_offset):
    time_delta, sign = get_time_offset(time_offset)
    if sign == 0:
        readable_time_str = ["unknown time zone"] * len(timestamp_int_list)
    else:
        # print(timestamp_int_list)
        timestamp_int_list_nat = timestamp_int_list.replace({"-1": nat})
        # timestamp_int_list_nat = [nat if x == -1 else x for x in list(timestamp_int_list)]
        timestamp_naive_list = pd.to_datetime(timestamp_int_list_nat, unit='ms', errors='ignore')
        # print(timestamp_naive_list)
        converter = lambda x: x + sign * time_delta if not pd.isnull(x) else x
        timestamp_TZaware_list = list(map(converter, timestamp_naive_list))
        translator = lambda x: x.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] if not pd.isnull(x) else x
        readable_time_str = pd.Series(map(translator, timestamp_TZaware_list))
        readable_time_str.replace({nat: "-1"}, inplace=True)
    return readable_time_str


if __name__ == "__main__":
    sample_csv_path = r"E:\compliance_analysis\prompt_response\aditya4_internal@timestudy_com\appended_response\aditya4_internal@timestudy_com_uEMA_2020-06-07.csv"
    time_zone = "GMT-04:00"
    df = pd.read_csv(sample_csv_path)
    print(convert_timestamp_int_list_to_readable_time(df['Response_Timestamp'], time_zone))
    # print("{} is translated to {} .".format(str(timestamp_int), convert_timestamp2string(timestamp_int, time_zone)))
