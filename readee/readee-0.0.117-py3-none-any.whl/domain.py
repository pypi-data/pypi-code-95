#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .common import _findRawContent
from telegram_util import parseDomain

def _findDomain(soup, url):
	for meta in soup.find_all('meta'):
		for att in meta.attrs:
			if 'url' in att.lower():
				r = parseDomain(meta[att])
				if r:
					return r
	for meta in soup.find_all('meta'):
		if 'url' in str(meta).lower():
			r = parseDomain(_findRawContent(meta))
			if r:
				return r
	return parseDomain(url)