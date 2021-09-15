#!/usr/bin/python
# -*- coding: utf-8 -*-

__copyright__ = """

MIT License

Copyright (c) 2021 Samapriya Roy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


"""
__license__ = "MIT License"

import requests
import json
import sys
import pkg_resources
import argparse
import os
from os.path import expanduser
from bs4 import BeautifulSoup


class Solution:
    def compareVersion(self, version1, version2):
        versions1 = [int(v) for v in version1.split(".")]
        versions2 = [int(v) for v in version2.split(".")]
        for i in range(max(len(versions1), len(versions2))):
            v1 = versions1[i] if i < len(versions1) else 0
            v2 = versions2[i] if i < len(versions2) else 0
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
        return 0


ob1 = Solution()

# Get package version
def pynative_version():
    url = "https://pypi.org/project/pynative/"
    source = requests.get(url)
    html_content = source.text
    soup = BeautifulSoup(html_content, "html.parser")
    company = soup.find("h1")
    vcheck = ob1.compareVersion(
        company.string.strip().split(" ")[-1],
        pkg_resources.get_distribution("pynative").version,
    )
    if vcheck == 1:
        print(
            "\n"
            + "========================================================================="
        )
        print(
            "Current version of pynative is {} upgrade to lastest version: {}".format(
                pkg_resources.get_distribution("pynative").version,
                company.string.strip().split(" ")[-1],
            )
        )
        print(
            "========================================================================="
        )
    elif vcheck == -1:
        print(
            "\n"
            + "========================================================================="
        )
        print(
            "Possibly running staging code {} compared to pypi release {}".format(
                pkg_resources.get_distribution("pynative").version,
                company.string.strip().split(" ")[-1],
            )
        )
        print(
            "========================================================================="
        )


pynative_version()


### download source

def source(mtype,path):
    if mtype =='territories':
        url = 'https://coordinates.native-land.ca/indigenousTerritories.json'
    elif mtype == 'languages':
        url = 'https://coordinates.native-land.ca/indigenousLanguages.json'
    elif mtype == 'treaties':
        url = 'https://coordinates.native-land.ca/indigenousTreaties.json'
    else:
        sys.exit('No matching map type found')
    response = requests.get(url,allow_redirects=True)
    if response.status_code == 200:
        print(f'Downloading to {path}')
        open(path, 'wb').write(response.content)
    else:
        print(f'Download failed with error code: {response.status_code}')

def fetch_from_parser(args):
    source(mtype=args.mtype,path=args.path)



def main(args=None):
    parser = argparse.ArgumentParser(description="Simple CLI for Native-Land API")
    subparsers = parser.add_subparsers()

    parser_fetch = subparsers.add_parser(
        "fetch", help="Download most updated map and type as GeoJSON file"
    )
    required_named = parser_fetch.add_argument_group(
        "Required named arguments."
    )
    required_named.add_argument("--mtype", help="Map type territories|languages|treaties", required=True)
    required_named.add_argument("--path", help="Full path to map.geojson", required=True)
    parser_fetch.set_defaults(func=fetch_from_parser)

    args = parser.parse_args()

    try:
        func = args.func
    except AttributeError:
        parser.error("too few arguments")
    func(args)


if __name__ == "__main__":
    main()
