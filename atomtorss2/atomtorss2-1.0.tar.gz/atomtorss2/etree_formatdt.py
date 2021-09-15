#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Date format converter for ElementTree XSLT

"""
__author__ = 'Frederic Laurent'
__version__ = "1.0"
__copyright__ = 'Copyright 2017, Frederic Laurent'
__license__ = "MIT"

import arrow
from lxml import etree


def convert(isodate):
    dt = arrow.get(isodate).datetime
    return dt.strftime('%a, %d %b %Y %H:%M:%S %z')


class DateISO_RFC822Converter(etree.XSLTExtension):
    """
        Convert ISO Date to RFC 822 Date
        ISO     : 2017-11-03T16:55:03.198512+00:00
        RFC 822 : Fri, 3 Nov 2017 16:55:03 +0000
    """

    def execute(self, context, self_node, input_node, output_parent):
        output_parent.text = convert(input_node.text)
