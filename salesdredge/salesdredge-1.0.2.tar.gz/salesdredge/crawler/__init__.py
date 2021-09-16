from salesdredge.crawler.scraper import scrape, process_page
from elasticsearch.helpers import bulk

from datetime import datetime

class Crawler:

    def __init__(self, connection, custom_func=None):
        self.custom_func = custom_func
        self.connection = connection


    def crawl_list(self, url_list):
        pages = []

        for url in url_list:
            p = scrape(url)
            p = process_page(p, custom_func=self.custom_func)
            pages.append(p)



        return pages


    def index_list(self, documents, index):

        now = datetime.now().astimezone()
        docs = []
        for doc in documents:

            for link in doc['links']:

                if link['tag'] == 'a' and link['url']['scheme'] not in ['mailto', 'sms', 'tel']:
                    link_doc = {
                        "scraped": False,
                        "error": False,
                        "id": link['id'],
                        "url": link['url'],
                        "text": link['text'],
                        "added": now.isoformat()
                    }

                    link_doc={
                        '_index': index,
                        '_id': link_doc['id'],
                        '_source': link_doc,
                        "_op_type": "create",

                    }
                    docs.append(link_doc)



            doc['added'] = now.isoformat()
            doc = {
                '_index': index,
                '_id': doc['id'],
                '_source': doc,
                "doc_as_upsert": True

            }
            docs.append(doc)
            bulk(self.connection, docs, index=index, raise_on_error=False)



