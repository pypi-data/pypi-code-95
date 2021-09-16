import os

def print_file():
    """It's will print the file path"""
    print("----")
    print(os.path.abspath(os.path.dirname(__file__)))

import sys
def pypath():
    """It's will print paths"""
    print('\n'.join(sys.path))


import csv
import pkg_resources

DATA_PATH = pkg_resources.resource_filename('widen', 'data')

def print_rows():
    with open(DATA_PATH+"/addresses.csv", "r") as f:
        reader = csv.reader(f, delimiter="\t")
        for i, line in enumerate(reader):
            print('line[{}] = {}'.format(i, line))