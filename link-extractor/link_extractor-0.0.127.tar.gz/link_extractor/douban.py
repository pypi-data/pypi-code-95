from telegram_util import matchKey

def getDoubanId(link):
	if not matchKey(link, ['note', 'group/topic', 'status', 'album']):
		return
	if matchKey(link, ['notes', 'statuses']):
		return
	if 'http' not in link:
		return
	parts = link.split('/')
	for part in parts[:-1]:
		try:
			int(part)
			return part
		except:
			...

def countLike(link, soup):
	douban_id = getDoubanId(link)
	result = 0
	for item in soup.find_all():
		if item.attrs and douban_id in str(item.attrs):
			result += int(item.get('data-count') or 0)
			try:
				result += int(item.parent.parent.find('td', class_='r-count').text)
			except:
				...
	return result

def getLimit(site):
	if '/explore' in site:
		return 120
	if '/blabla' in site: # 鹅组
		return 200
	if '/group/' in site:
		return 200
	return -1

def getDoubanLinks(site, links, soup):
	counted_items = [(countLike(link, soup), link) for link in links
		if getDoubanId(link)]
	counted_items.sort(reverse=True)
	limit = getLimit(site)
	return [item[1] for item in counted_items if item[0] > limit]