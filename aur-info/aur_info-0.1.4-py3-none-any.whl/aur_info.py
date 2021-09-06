#!/bin/python

import os
import sys
import getopt
import requests as r
from bs4 import BeautifulSoup as bs

if __name__ == '__main__':
    av = sys.argv[1:]
    opts, a = getopt.getopt(av, "hp:", ['help','pkg='])

    args = {}
    for opt in opts:
        if opt[0] in ['-h', '--help']:
            args.update({'help':True})
        if opt[0] in ['-p', '--pkg']:
            args.update({'pkg':opt[1]})

    if 'help' in args:
        print('Usage: aur-info -p <exact_package_name>')
        sys.exit(0)

    if 'pkg' not in args:
        raise Exception('Please specify a package name. It should be an exact match. Use aur-search if needed.')
    res = r.get('https://aur.archlinux.org/packages/{}'.format(args['pkg']))

    if res.ok:
        b = bs(res.text, 'html.parser')
        description=b.body.table.findChildren("tr")[2].td.text
        git_url=b.body.table.findChildren("tr")[0].td.a.text
        submitted=b.body.table.findChildren("tr")[11].td.text
        updated=b.body.table.findChildren("tr")[12].td.text
        print('\nName:')
        print('-----')
        print(args['pkg'].capitalize())
        print('\nDescription:')
        print('------------')
        print(description)
        print('\nSubmitted:')
        print('----------')
        print(submitted)
        print('Updated:')
        print('---------')
        print(updated)
        print('\nRepository:')
        print('-----------')
        print(git_url)
        #os.system('git clone {}'.format(git_url))
    else:
        raise Exception("Package not found. Please check to see if there exists a match.")
