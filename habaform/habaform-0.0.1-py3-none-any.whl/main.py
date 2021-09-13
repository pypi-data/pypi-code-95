#!/usr/bin/env python3
import argparse
import os
from .parse import parse
from .plan import plan
from .apply import apply

def main():
    arg_parser = argparse.ArgumentParser(description='Habaform')
    arg_parser.add_argument('Method',metavar='method',type=str,help='parse,plan or apply')
    args = arg_parser.parse_args()
    
    harbor_username = os.environ['HARBOR_USERNAME']
    harbor_password = os.environ['HARBOR_PASSWORD']
    harbor_url = os.environ['HARBOR_URL']

    print(args.Method)

    if args.Method == "parse":
        print('Parsing {}'.format(harbor_url))
        parse(harbor_username,harbor_password,harbor_url)

    if args.Method == "plan":
        plan(harbor_username,harbor_password,harbor_url)

    if args.Method == "apply":
        habadiff_dict = plan(harbor_username,harbor_password,harbor_url)
        apply(harbor_username,harbor_password,harbor_url,habadiff_dict)
