#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Transform Atom v1 Feed to RSS v2 using XSLT (ElementTree)

"""
__author__ = 'Frederic Laurent'
__version__ = "1.0"
__copyright__ = 'Copyright 2017, Frederic Laurent'
__license__ = "MIT"

import os.path
import re
import sys

from lxml import etree

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from atomtorss2 import etree_formatdt


class ImportLocalResolver(etree.Resolver):
    def __init__(self, rootdir, *args, **kwargs):
        super(ImportLocalResolver, self).__init__(*args, **kwargs)
        self.rootdir = rootdir
        self.prefix = "file://"

    def resolve(self, url, pubid, context):
        if url.startswith(self.prefix):
            fname = os.path.join(self.rootdir, url[len(self.prefix):])
            # we can call resolve_filename but etree doesn't known how to deal with XSLT2 func : format-dateTime(
            # return self.resolve_filename(fname,context)

            # so we suppress (hack) the call of this function
            # select="format-dateTime(..." becomes select="."
            with open(fname, "r") as fin:
                data = fin.read()
                data = re.sub('select="format-dateTime\(.*?"', 'select="."', data)
                return self.resolve_string(data, context)


class Processor:
    def __init__(self, xslt_tree=None):
        self.xslt = xslt_tree
        self.extensions = {}

    def register(self, ext_ns, ext_func, func_inst):
        self.extensions[(ext_ns, ext_func)] = func_inst

    def transform(self, xml_tree):
        if self.xslt is not None:
            transform = etree.XSLT(self.xslt, extensions=self.extensions)
            result_xml = transform(xml_tree)
            return result_xml
        else:
            print("No XSLT loaded.")
            return None


class DateFormatterProcessor(Processor):
    XSLT_EXT_NS = 'http://www.opikanoba.org/ns/etree-extensions'
    XSLT_EXT_FUNC = 'formatdt'

    def __init__(self, xslt_tree=None):
        Processor.__init__(self, xslt_tree)
        self.register(DateFormatterProcessor.XSLT_EXT_NS,
                      DateFormatterProcessor.XSLT_EXT_FUNC,
                      etree_formatdt.DateISO_RFC822Converter())

    def load_xslt(self, xslt_filename):
        _parser = etree.XMLParser()
        filedir = os.path.dirname(os.path.abspath(xslt_filename))
        _parser.resolvers.add(ImportLocalResolver(filedir))
        self.xslt = etree.parse(xslt_filename, _parser)
