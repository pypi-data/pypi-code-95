#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Processes Atom file and Produces RSS 2 file

"""
__author__ = 'Frederic Laurent'
__version__ = "1.0"
__copyright__ = 'Copyright 2017, Frederic Laurent'
__license__ = "MIT"

import argparse
import codecs
import os.path
import xslt_ext
from lxml import etree

from __init__ import *

ENCODING = 'utf-8'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--atom", help="Atom filename (input)")
    parser.add_argument("--rss2", help="RSS2 filename (output)")
    parser.add_argument("--xslt", help="XSLT stylesheet (optionnal), default = {}".format(DEFAULT_XSLT_FILE),
                        default=DEFAULT_XSLT_FILE)

    args = parser.parse_args()

    filedir = os.path.dirname(os.path.abspath(__file__))
    xslt_filename = os.path.join(filedir, args.xslt)

    print("XSLT : {}".format(xslt_filename))

    proc = xslt_ext.DateFormatterProcessor()
    proc.load_xslt(xslt_filename)

    if args.atom is not None and os.path.exists(args.atom):
        result_xml = proc.transform(etree.parse(args.atom))
        data = etree.tostring(result_xml, encoding=ENCODING, xml_declaration=True, pretty_print=True)

        if args.rss2 is not None:
            with codecs.open(args.rss2, "w", ENCODING) as fout:
                fout.write(data.decode(ENCODING))
        else:
            print(data)


if __name__ == "__main__":
    main()
