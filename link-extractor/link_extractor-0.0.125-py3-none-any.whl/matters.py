from bs4 import BeautifulSoup
import cached_url

def getLikes(link):
	soup = BeautifulSoup(cached_url.get(link), 'html.parser')
	item = soup.find('span', class_="clap").nextSibling
	if item:
		return int(item.text)
	else:
		return 0

def filterMatters(links):
	for link in links:
		if getLikes(link) > 300:
			yield link
