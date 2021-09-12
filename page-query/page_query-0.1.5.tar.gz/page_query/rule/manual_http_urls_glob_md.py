import glob
import logging
import re
import requests
import yaml
import hashlib

from pathlib import Path
from typing import Dict, List


class ManualHttpUrlsGlobMarkdown:

    file_name_validator = re.compile('([a-zA-Z0-9]+)(_([a-zA-Z0-9]+))*[.]md')
    meta_begin_mark = '```yaml'
    meta_end_mark = '```'

    def __init__(self, patterns: List[str], tags: List[str]) -> None:
        self._patterns = patterns
        self._tags = tags
        self._pages = []

        for pattern in self._patterns:
            for path in glob.glob(pattern):
                info = self.load_and_parse(Path(path))

                md5 = hashlib.md5()
                md5.update(info['title'].encode('utf-8'))
                md5.update(','.join(info['tags']).encode('utf-8'))
                md5.update(info['summary'].encode('utf-8'))
                md5.update('\n'.join(info['urls']).encode('utf-8'))
                self._pages.append((md5.hexdigest(), info))
    
    def page_ids(self):
        for page in self._pages:
            yield page[0]

    def pages(self, filter=set()):
        for page in self._pages:
            if page[0] not in filter:
                body = []
                for url in page[1].get('urls', []):
                    r = requests.get(url)
                    if r.status_code != 200:
                        logging.warning(f'failed to request {url}, status code: {r.status_code}')
                    else:
                        body.append(r.text)
                page[1]['body'] = body
                yield page
    
    def load_and_parse(self, path: Path) -> Dict:
        logging.info(f'load and parse {path}')
        r = self.file_name_validator.fullmatch(path.name)
        if r is None:
            raise ValueError(f'{path.name} is not a valid file name')

        title = path.name[:-3].replace('_', ' ')
        file_content = path.read_text().strip()
        if not file_content.startswith(self.meta_begin_mark):
            raise ValueError(f'{file_content[:len(self.meta_begin_mark) + 10]}'
                              ' is not begin with {self.meta_begin_mark}')
        
        file_content = file_content[len(self.meta_begin_mark):]
        end = file_content.find(self.meta_end_mark)
        if end == -1:
            raise ValueError(f'file_content has no {self.meta_end_mark}')

        meta_content = file_content[:end]
        file_content = file_content[end+len(self.meta_end_mark):].strip()

        if len(meta_content) == 0:
            ret = {}
        else:
            ret = yaml.safe_load(meta_content)
        if 'title' not in title:
            ret['title'] = title
        ret['summary'] = file_content
        ret['tags'] = ret.pop('tags') + self._tags
        ret['urls'] = ret.pop('http_urls', [])
        return ret

    def __str__(self) -> str:
        return ','.join(self._patterns)