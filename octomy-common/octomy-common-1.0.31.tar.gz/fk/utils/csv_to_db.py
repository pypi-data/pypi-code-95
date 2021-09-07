from Database import Database
from Influx import Influx
from queue import Queue
from ScraperFactory import ScraperFactory
import credentials
import json
import os
import pprint
import re
import sys
import time
import utils
import base64
import csv
import datetime


# def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
# 	csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
# 	for row in csv_reader:
# 		yield [unicode(cell, 'ISO-8859-1') for cell in row]


# Main entrypoint of script
if __name__ == "__main__":
    # Change current working dir to that of this script's location
    cwd = os.path.dirname(os.path.realpath(__file__))
    os.chdir(cwd)
    print("Set working dir to " + cwd)

    # Load credentials
    credentials = credentials.load_credentials()
    if not credentials:
        sys.exit(1)

    print("#############################################################################")

    db = Database(credentials)

    # File containting one shop name per line
    oh_no_fn = "oh_no.csv"

    # reader = unicode_csv_reader(open(oh_no_fn))

    # for site_id in reader:		print(site_id)

    map = {"Comment": "comment", "Api Key": "api_key", "Created At": "created_at", "Fetched At": "fetched_at", "Fetched Count": "fetched_count", "Link": "link", "Sale Date First": "sale_date_first", "Sale Date First Ever": "sale_date_first_ever", "Sale Date Last": "sale_date_last", "Site Id": "site_id", "Spread": "spread"}

    # sys.exit(1)
    with open(oh_no_fn) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter="\t")
        line_count = 0
        headers = []
        for row in csv_reader:
            if line_count == 10:
                # break
                pass
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                headers = row
                line_count += 1
            else:
                spop = {}
                for index, header in enumerate(headers):
                    h = map.get(header, header)
                    v = row[index]
                    if v == "":
                        v = None
                    elif h.startswith("sale_date_"):
                        v = datetime.datetime(v)
                    spop[h] = v
                i = db.upsert_spop_id(spop)
                # print(f"LINE:{spop} ---> {i}")
                line_count += 1
        print(f"Processed {line_count} lines.")
