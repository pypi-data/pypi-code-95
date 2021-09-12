import requests
import logging
import hashlib

from typing import Dict, List


class ManualHttpUrls:

    def __init__(self, title: str, tags: List[str],
                       summary: str, http_urls: List[str]) -> None:
        self._title = title
        self._tags = tags
        self._summary = summary
        self._http_urls = http_urls

        md5 = hashlib.md5()
        md5.update(title.encode('utf-8'))
        md5.update(','.join(tags).encode('utf-8'))
        md5.update(summary.encode('utf-8'))
        md5.update('\n'.join(http_urls).encode('utf-8'))
        self._id = md5.hexdigest()

    def page_ids(self):
        yield self._id

    def pages(self, filter=set()) -> Dict:
        if self._id in filter:
            return

        body = []
        for url in self._http_urls:
            r = requests.get(url)
            if r.status_code != 200:
                logging.warning(f'failed to request {url}, status code: {r.status_code}')
            else:
                body.append(r.text)
        yield self._id, {
            'title': self._title,
            'tags': self._tags,
            'summary': self._summary,
            'body': body,
            'urls': self._http_urls
        }

    def __str__(self) -> str:
        return self._title