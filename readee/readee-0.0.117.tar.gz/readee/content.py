#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from .common import _findRawContent
from .domain import _findDomain
from .final_touch import _finalTouch
from .images import _cleanupImages
from .inner_article import _getInnerArticle
from .link import _replaceOfftopicLink
from .offtopic import _decomposeOfftopic
from .tag_replace import _tagReplace
from telegram_util import matchKey
import sys
import os

def saveSoup(soup, stage):
	if 'debug' in str(sys.argv):
		os.system('mkdir tmp > /dev/null 2>&1')
		with open("tmp/%d.html" % stage, 'w') as f:
			f.write(str(soup))

def _findMainFromSoup(soup, url, args = {}):
	domain = _findDomain(soup, url)
	saveSoup(soup, 0)
	soup = _replaceOfftopicLink(soup, args)
	saveSoup(soup, 1)
	soup = _decomposeOfftopic(soup, url, args)
	saveSoup(soup, 2)
	soup = _cleanupImages(soup, domain)
	saveSoup(soup, 3)
	soup, before_content = _getInnerArticle(soup, domain)
	saveSoup(soup, 4)
	soup = _tagReplace(soup)
	saveSoup(soup, 5)
	soup = _finalTouch(soup, url)
	saveSoup(soup, 6)
	return soup

def _findMain(soup, doc, url, args = {}):
	result = _findMainFromSoup(soup, url, args)
	if result and result.text and result.text.strip():
		return result
	result = _findMainFromSoup(BeautifulSoup(str(doc.content), features="html.parser"), url, args)
	if result and result.text and result.text.strip():
		return result
	return doc.content()