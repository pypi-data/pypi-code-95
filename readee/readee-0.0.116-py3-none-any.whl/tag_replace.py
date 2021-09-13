#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .common import _copyB, fact
from bs4 import BeautifulSoup
from telegram_util import matchKey

def _tagReplace(soup, args = {}):
	wrap_with_i = [
		soup.find_all("div"),
		soup.find_all("span"),
		soup.find_all("p"),
	]
	for l in wrap_with_i:
		for item in l:
			attrs = str(item.attrs)
			attrs = attrs.replace(": ", ":")
			if 'font-style:italic' in attrs:
				wrapper = fact().new_tag("i")
				wrapper.append(_copyB(item))
				item.replace_with(wrapper)
	wrap_with_p = [
		soup.find_all("div", class_="article-paragraph"),
		soup.find_all("section"),
		[x for x in soup.children if isinstance(x, str) and x[:3] != 'doc'],
	]
	for l in wrap_with_p:
		for item in l:
			wrapper = fact().new_tag("p")
			wrapper.append(_copyB(item))
			item.replace_with(wrapper)
	for l in soup.find_all("p"):
		children = list(l.children)
		if len(children) >= 1 and isinstance(children[0], str):
			children[0].replace_with(children[0].lstrip())
		if len(children) != 1 or not isinstance(children[0], str):
			continue
		to_replace = None
		if l.parent.name == 'blockquote': # douban status specific
			to_replace = l.parent
		if matchKey(str(l.parent.attrs), ['review-content', 'note']): # douban reviews.notes specific
			to_replace = l
		if not to_replace or len(list(to_replace.children)) != 1:
			continue
		paragraphs = ''.join(['<p>%s</p>' % x for x in children[0].split('\n') 
			if x.strip()])
		to_replace.replace_with(BeautifulSoup("<p>%s</p>" % paragraphs, features="lxml"))
	if args.get('list_replace'):
		to_remove_tags = [
			soup.find_all("li"),
			soup.find_all("ul")
		]
		for l in to_remove_tags:
			for item in l:
				item.name = p
	return soup