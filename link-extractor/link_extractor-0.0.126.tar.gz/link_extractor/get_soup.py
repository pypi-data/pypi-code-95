from bs4 import BeautifulSoup
import cached_url
from telegram_util import matchKey

offtopic_tags = ['nav', 'footer', 'aside', 'header']
try:
	credential = yaml.load('credential', Loader=yaml.FullLoader)
except:
	credential = {}

def getSoup(site):
	if 'douban.' in site and 'douban_cookie' in credential:
		option = {'cookie': credential.get('douban_cookie')}
	else:
		option = {}
	soup = BeautifulSoup(cached_url.get(site, option), 'html.parser')
	for item in soup.find_all('a', rel='author'):
		item.decompose()
	for tag in offtopic_tags:
		for item in soup.find_all(tag):
			item.decompose()
	if 'freewechat.com' in site:
		for item in soup.find_all('div', id='hot-articles'):
			item.decompose()
	return soup