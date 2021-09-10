import csv
import pkg_resources
from random import choice

csvquotes = pkg_resources.resource_filename('quotebot', 'quotes.csv')

with open(csvquotes, 'r') as f:
    reader = csv.reader(f)
    QUOTES = [line for line in reader]

def enlightme():
    quote = choice(QUOTES)
    return quote


