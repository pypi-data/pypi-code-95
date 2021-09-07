import argparse
from datetime import datetime, timedelta
import pathlib
"""The program displays the rating of the tournament participants"""


def parse_files(start, end, abbreviations):
    """Function for parsing files with participant data

    Reads all files, converts text to objects and adds
    data to a dictionary"""
    pilots = {}
    date_template = '%Y-%m-%d_%H:%M:%S.%f'

    for line in start:
        date_start = datetime.strptime(line[3:-1], date_template)
        pilots[line[:3]] = {'start_time': date_start}

    for line in end:
        date_end = datetime.strptime(line[3:-1], date_template)
        pilots[line[:3]]['end_time'] = date_end

    for line in abbreviations:
        key, name, company = line.split('_')
        pilots[line[:3]]['racer_name'] = name
        pilots[line[:3]]['company'] = company.replace('\n', '')

    return pilots


def build_report(pilots, reverse=False):
    """Sorts by lap time

    Reads a data dictionary, calculates lap times
    and sorts by lap times"""
    abbr_racer = []

    for key in pilots:
        lap_time = pilots[key]['end_time'] - pilots[key]['start_time']
        pilots[key]['lap_time'] = lap_time

    sorted_abbr = sorted(
        pilots,
        key=lambda pilot: pilots[pilot].get('lap_time') if pilots[pilot].get('lap_time').days >= 0
        else timedelta(days=1),
        reverse=reverse
    )

    for element in sorted_abbr:
        abbr_racer.append(pilots[element])

    return abbr_racer


def print_report(abbr_racer):
    """Function for forming the standings

    Handles lap time errors, returns a list with the data
    of the riders in the given sequence"""
    standings = []

    for counter, elements in enumerate(abbr_racer):

        if elements['lap_time'].days >= 0:
            edited_data = str(elements["lap_time"])[2:-3]
            standings.append(f'{elements["racer_name"]} | {elements["company"]} | {edited_data}')
        else:
            standings.append(f'{elements["racer_name"]} - Error')

        if counter == 14:
            standings.append(f'------------------------------------------')

    return '\r\n'.join(standings)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--files', type=pathlib.Path, required=True)
    parser.add_argument('--asc', action='store_true')
    parser.add_argument('--desc', action='store_true')
    parser.add_argument('--driver', type=str)

    arguments = parser.parse_args()

    start = list(arguments.files.glob('start.log')).pop()
    end = list(arguments.files.glob('end.log')).pop()
    abbreviations = list(arguments.files.glob('abbreviations.txt')).pop()

    data = parse_files(start.open(), end.open(), abbreviations.open())
    if arguments.asc and arguments.desc:
        raise ValueError('Should be one argument --asc or --desc')

    if arguments.desc:
        reversing = True
    else:
        reversing = False

    if arguments.driver:
        for key, value in data.items():
            if arguments.driver == value['racer_name']:
                data = {key: value}
                break

    print(print_report(build_report(data, reversing)))
