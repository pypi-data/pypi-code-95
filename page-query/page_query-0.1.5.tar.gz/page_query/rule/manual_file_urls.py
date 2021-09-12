import hashlib
import logging

from typing import Dict, List
from pathlib import Path


class ManualFileUrls:

    def __init__(self, title: str, tags: List[str],
                       summary: str, file_urls: List[str]) -> None:
        self._title = title
        self._tags = tags
        self._summary = summary
        self._file_urls = file_urls

        md5 = hashlib.md5()
        md5.update(title.encode('utf-8'))
        md5.update(','.join(tags).encode('utf-8'))
        md5.update(summary.encode('utf-8'))
        md5.update('\n'.join(file_urls).encode('utf-8'))
        self._id = md5.hexdigest()
    
    def page_ids(self):
        yield self._id

    def pages(self, filter=set()):
        if self._id in filter:
            return

        body = []
        for url in self._file_urls:
            path = Path(url)            
            if not path.is_file():
                logging.warning(f'{path} is not file')
            else:
                body.append(path.read_text())
        yield self._id, {
            'title': self._title,
            'tags': self._tags,
            'summary': self._summary,
            'body': body,
            'urls': self._file_urls
        }
    
    def __str__(self) -> str:
        return self._title