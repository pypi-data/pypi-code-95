import yaml

start_pivot = 'ytInitialData = '
end_pivot = ';</script>'

def getYoutubeLinks(soup):
	json = str(soup).split(start_pivot)[1].split(end_pivot)[0]
	content = yaml.load(json, Loader=yaml.FullLoader)
	queue = [content]
	result = set()
	while queue:
		item = queue.pop()
		if isinstance(item, list):
			for sub_item in item:
				queue.append(sub_item)
		elif isinstance(item, dict):
			for _, sub_item in item.items():
				queue.append(sub_item)
			if item.get('videoId'):
				result.add(item.get('videoId'))
	return ['https://www.youtube.com/watch?v=' + item for item in result]