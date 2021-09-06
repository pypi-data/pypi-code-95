#!/bin/python

def get_info(pkg_name):
    import requests as r
    from bs4 import BeautifulSoup as bs

    pkg = {}
    res = r.get('https://aur.archlinux.org/packages/{}'.format(pkg_name))
    if not res.ok:
        return None
    b = bs(res.text, 'html.parser')
    pkg['name']=pkg_name.capitalize()
    pkg['description']=b.body.table.findChildren("tr")[2].td.text
    pkg['git_url']=b.body.table.findChildren("tr")[0].td.a.text
    pkg['submitted']=b.body.table.findChildren("tr")[11].td.text
    pkg['updated']=b.body.table.findChildren("tr")[12].td.text
    return pkg

if __name__ == '__main__':
import os
import sys
import getopt

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

    pkg = get_info(args['pkg'])
    if pkg:
        print('\nName:')
        print('-----')
        print(pkg['name'])
        print('\nDescription:')
        print('------------')
        print(pkg['description'])
        print('\nSubmitted:')
        print('----------')
        print(pkg['submitted'])
        print('Updated:')
        print('---------')
        print(pkg['updated'])
        print('\nRepository:')
        print('-----------')
        print(pkg['git_url'])
    else:
        raise Exception("Package not found. Please check to see if there exists a match.")
