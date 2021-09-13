#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from readability import Document
from .content import _findMain
import cached_url

TO_REMOVE = [
	'跳到导航', 
	'跳到搜索', 
	'Skip to main content'
]

def _trimWebpage(raw):
	for to_remove in TO_REMOVE:
		raw = raw.replace(to_remove, '')
	for anchor in ['<!-- detail_toolbox -->', '<!--article_adlist']:
		index = raw.find(anchor)
		if index != -1:
			raw = raw[:index]
	return raw

def getArticle(url, content, args = {}):
	if not content:
		content = cached_url.get(url)
	soup = BeautifulSoup(_trimWebpage(content), 'html.parser')
	doc = Document(content)
	return _findMain(soup, doc, url, args)

