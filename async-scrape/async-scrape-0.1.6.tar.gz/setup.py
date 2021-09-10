# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['async_scrape', 'async_scrape.libs']

package_data = \
{'': ['*']}

install_requires = \
['PyPAC>=0.15.0,<0.16.0',
 'aiohttp>=3.7.4,<4.0.0',
 'asyncio>=3.4.3,<4.0.0',
 'nest-asyncio>=1.5.1,<2.0.0',
 'pandas>=1.3.2,<2.0.0',
 'requests-html>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'async-scrape',
    'version': '0.1.6',
    'description': 'A package designed to scrape webpages using aiohttp and asyncio. Has some error handling to overcome common issues such as sites blocking you after n requests over a short period.',
    'long_description': '# Async-scrape\n## _Perform webscrape asyncronously_\n\n[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)\n\nAsync-scrape is a package which uses asyncio and aiohttp to scrape websites and has useful features built in.\n\n## Features\n\n- Breaks - pause scraping when a website blocks your requests consistently\n- Rate limit - slow down scraping to prevent being blocked\n\n\n## Installation\n\nAsync-scrape requires [C++ Build tools](https://go.microsoft.com/fwlink/?LinkId=691126) v15+ to run.\n\n\n```\npip install async-scrape\n```\n\n## How to use it\n```\n#Create an instance\nfrom async_scrape import AsyncScrape\n\ndef post_process(resp):\n    """Function to process the gathered response from the request"""\n    if resp.status == 200:\n        return "Request worked"\n    else:\n        return "Request failed"\n\nasync_Scrape = AsyncScrape(\n    post_process_func=post_process,\n    post_process_kwargs={},\n    fetch_error_handler=None,\n    use_proxy=False,\n    proxy=None,\n    pac_url=None,\n    acceptable_error_limit=100,\n    attempt_limit=5,\n    rest_between_attempts=True,\n    rest_wait=60\n)\n\nurls = [\n    "https://www.google.com",\n    "https://www.bing.com",\n]\n\nresps = async_Scrape.scrape_all(urls)\n```\n\nResponse object is a list of dicts in the format:\n```\n{\n    "url":url, #url of request\n    "func_resp":func_resp, #response from post processing function\n    "status":resp.status, #http status\n    "error":None #any error encountered\n}\n```\n\n\n## License\n\nMIT\n\n**Free Software, Hell Yeah!**\n\n[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn\'t be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)\n\n   [dill]: <https://github.com/joemccann/dillinger>\n   [git-repo-url]: <https://github.com/joemccann/dillinger.git>\n   [john gruber]: <http://daringfireball.net>\n   [df1]: <http://daringfireball.net/projects/markdown/>\n   [markdown-it]: <https://github.com/markdown-it/markdown-it>\n   [Ace Editor]: <http://ace.ajax.org>\n   [node.js]: <http://nodejs.org>\n   [Twitter Bootstrap]: <http://twitter.github.com/bootstrap/>\n   [jQuery]: <http://jquery.com>\n   [@tjholowaychuk]: <http://twitter.com/tjholowaychuk>\n   [express]: <http://expressjs.com>\n   [AngularJS]: <http://angularjs.org>\n   [Gulp]: <http://gulpjs.com>\n\n   [PlDb]: <https://github.com/joemccann/dillinger/tree/master/plugins/dropbox/README.md>\n   [PlGh]: <https://github.com/joemccann/dillinger/tree/master/plugins/github/README.md>\n   [PlGd]: <https://github.com/joemccann/dillinger/tree/master/plugins/googledrive/README.md>\n   [PlOd]: <https://github.com/joemccann/dillinger/tree/master/plugins/onedrive/README.md>\n   [PlMe]: <https://github.com/joemccann/dillinger/tree/master/plugins/medium/README.md>\n   [PlGa]: <https://github.com/RahulHP/dillinger/blob/master/plugins/googleanalytics/README.md>\n',
    'author': 'Robert Franklin',
    'author_email': 'cia05rf@gmail.com',
    'maintainer': 'Robert Franklin',
    'maintainer_email': 'cia05rf@gmail.com',
    'url': 'https://github.com/cia05rf/async-scrape/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
