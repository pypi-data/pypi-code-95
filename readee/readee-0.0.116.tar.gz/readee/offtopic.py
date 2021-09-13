#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram_util import matchKey
from .common import fact, _wrap
from .images import _yieldPossibleImg
from bs4 import Comment
import sys

OFFTOPIC_TAG = ['small', 'address', 'meta', 'script', 'sup', 'svg']

OFFTOPIC_ATT = [
	'latest', 'more', 'facebook', 'ts-fab-wrapper',
	'cn-carousel-medium-strip', 'video__end-slate__top-wrapper', 'metadata', 
	'el__article--embed', 'signup', 'related', 'disclaimer', 'off-screen', 
	'story-body__unordered-list', 'story-image-copyright', 'article-header', 
	'top-wrapper', 'bottom-of-article', 'bottom-wrapper', 'linkList', 
	'display:none;', 'accordion', 'el-editorial-source', 'video__end-slate__tertiary-title',
	'adblocker', 'tagline', 'navmenu', 'topHeader', 'Post Bottom',
	't_callout', 'add-interest', 'bb-newsletter', 'popover', 'toast', 'after-article', 
	'submeta', 'rich-link__container', 'content__meta-container', 'mw-editsection',
	'noprint', 'jump-to-nav', 'toctitle', 'reflist', 'contentSub',
	'参考文献', '引用', '网页', 'printfooter', 'catlinks', 'Post Bottom',
	'ad-unit', 'box-ad', "class : ['tabs']", "class : ['hd']", 'NYT_BELOW_MAIN_CONTENT_REGION',
	'NYT_TOP_BANNER_REGION', 'g-inlineguide', 'entry-meta-bar', 'extra-hatom-entry-title',
	'list-unstyled', 'hide_word', 'single-header', 'post-pagination',
	'weui-dialog', 'post-title', 'post-topic', 'byline-date', 'post-print',
	'mailing-list-popup', 'taxonomies', 'authors', 'interactive-content',
	'socialBTN', 'page-view', 'pn-single-post-wrapper__social', 'pn-pagicle-widget',
	'mashsb-container', 'give-form-wrap', 'story_bady_info_author',
	'taglist', 'donate', 'see-also', 'donation-box', 'license__Container',
	'field-photo-credit', 'Avatar', 'floating-share', 'meta-box', 'tag-list',
	'tools__ShareIconBlock', 'aside__Container', 'MetadataAndTool', 'DesktopAsideBlock',
	'StyledSeparationCurve', 'separation-curve', "['extending']", "['meta-tag']",
	'sharedaddy',
]

OFFTOPIC_ATT_WITH_EXCEPTION = {
	'sidebar': ['no-sidebar', 'one-sidebar', 'penci-main', 'id : page', 
		'single-post', 'has-sidebar', 'sidebar-off'],
	'hidden': ['lazy', 'false', 'label-hidden', 'rich_media_content', 'start', 'overflow', 'comment-hidden', 'ariahidden'],
	'navigation': ['navigation-', '-navigation'],
	'copyright': ['and'],
	'navbar': ['single-post'],
	'button': ['image-container', 'imageViewer', 'tabindex'],
	'footer': ['lodestar-footer-image']
}

OFFTOPIC_CLASSES = ['ads']

DIV_AD_WORDS = [
	'中文简报',
	'@nytimes',
	'NYT简报',
]

P_AD_WORDS = [
	'別忘了給點支持與讚賞，讓我知道創作的路上有你陪伴。',
	'一鍵登入，即可加入全球最優質中文創作社區',
	'The Times is committed', 
	'Follow The New York Times',
	'Love HuffPost',
	'discounted subscription today',
	'Just follow this link',
	'Share on WeChat / 在微信上分享这篇文章',
	'English version / 英文翻译'
]

def _isOffTopic(attrs):
	if not attrs:
		return 
	r = []
	for k, v in attrs.items():
		if k != 'data-component' and matchKey(k, ['href', 'src', 'url', 'alt', 'data', 'xmlns:fb']):
			continue
		r.append(str(k) + ' : ' + str(v))
	r = '\n'.join(r)
	for att in OFFTOPIC_ATT:
		if att in r:
			return att
	for att in OFFTOPIC_ATT_WITH_EXCEPTION:
		if att in r and not matchKey(r, OFFTOPIC_ATT_WITH_EXCEPTION[att]):
			return att
	return 

def _decompose(item):
	if 'offtopic' in str(sys.argv) and item.text and len(item.text) > 500:
		print('decomposing long text: ', item.attrs, ' '.join(item.text[:100].split()))
		if item.name in OFFTOPIC_TAG:
			print(item.name)
		if _isOffTopic(item.attrs):
			print(_isOffTopic(item.attrs))
	if 'imageViewer' in str(item):
		if item.name in OFFTOPIC_TAG:
			print(item.name)
		if _isOffTopic(item.attrs):
			print(_isOffTopic(item.attrs))
	item.decompose()

def _decompseAds(soup):
	for item in soup.find_all("div", class_="article-paragraph"):
		if matchKey(item.text, DIV_AD_WORDS):
			_decompose(item)
	for item in soup.find_all("p"):
		if matchKey(item.text, P_AD_WORDS) or item.text in ['广告']:
			_decompose(item)

def _decomposeOfftopic(soup, url, args = {}):
	for item in list(soup.find_all())[1:]:
		if _isOffTopic(item.attrs) or \
			item.name in OFFTOPIC_TAG:
			_decompose(item)

	for c in OFFTOPIC_CLASSES:
		for item in soup.find_all(class_=c):
			_decompose(item)

	if not matchKey(url, ['medium']):
		for item in soup.find_all('h1'):
			_decompose(item)

	_decompseAds(soup)

	for item in soup.find_all(string=lambda text: isinstance(text, Comment)):
		item.extract()

	for item in soup.find_all("header"):
		s = item.find("p", {"id": "article-summary"})
		img = next(_yieldPossibleImg(item), None)
		if not s or not s.text:
			if img:
				item.replace_with(img)
			else:
				_decompose(item)
			continue
		if not img:
			item.replace_with(s)
			continue
		cap = img.find('figcaption')
		if cap and not cap.text:
			cap.replace_with(_wrap('figcaption', s.text))
			item.replace_with(img)
			continue
		if not cap and img.name in ['div', 'figure']:
			img.append(_wrap('figcaption', s.text))
			item.replace_with(img)
			continue
		item.replace_with(_wrap('p', img, s))
	return soup