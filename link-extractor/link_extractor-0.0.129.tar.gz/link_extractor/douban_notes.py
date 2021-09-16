import yaml
import cached_url

def getDoubanNotes(uid):
	link = 'https://m.douban.com/rexxar/api/v2/user/%s/notes?start=0&count=20' % uid
	json = yaml.load(cached_url.get(link, headers={'referer': 'https://m.douban.com'}), Loader=yaml.FullLoader)
	for note_obj in json['notes']:
		yield note_obj['url'].replace('\/', '/')
