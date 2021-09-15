import argparse
import sys
from . import basketcase

def parse():
    parser = argparse.ArgumentParser(description='Fetch resources from Instagram.')
    parser.add_argument('session_id', help='The session cookie id')
    args = parser.parse_args()

    urls = []

    for line in sys.stdin:
        line = line.rstrip()

        if (line):
            urls.append(line)

    bc = basketcase.BasketCase(args.session_id)
    bc.fetch(urls)

if __name__ == '__main__':
    parse()

