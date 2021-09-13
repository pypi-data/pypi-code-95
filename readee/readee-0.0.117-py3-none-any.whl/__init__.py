#!/usr/bin/env python3
# -*- coding: utf-8 -*-

name = 'readee'

from .article import getArticle
from bs4 import BeautifulSoup
from opencc import OpenCC

cc = OpenCC('tw2sp')

def _formaturl(url):
	if '://' not in url:
		return "https://" + url
	return url

def export(url, content=None, **args):
	article = getArticle(url, content, args)
	if not article.text or not article.text.strip():
		raise Exception('Can not find main content')
	if args.get('toSimplified'):
		b = BeautifulSoup(str(article), 'html.parser')
		for x in b.findAll(text=True):
			x.replaceWith(cc.convert(x))
		return b
	return article