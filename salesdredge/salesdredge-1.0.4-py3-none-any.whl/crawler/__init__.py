from salesdredge.crawler.scraper import scrape, process_page
from elasticsearch.helpers import bulk
import resource
from datetime import datetime
import concurrent.futures


def limit_memory(maxsize):
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (maxsize, hard))



class Crawler:

    def __init__(self, connection, custom_func=None):
        self.custom_func = custom_func
        self.connection = connection

    def scrape(self, url):
        p = scrape(url)
        p = process_page(p, custom_func=self.custom_func)
        return p

    def crawl_list(self, url_list):

        giga_byte = 2 ** 30
        limit_memory(giga_byte)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.scrape, url) for url in url_list]
        pages = [x.result() for x in futures]
        return pages


    def index_list(self, documents, index):

        now = datetime.now().astimezone()
        docs = []
        for doc in documents:
            if doc['error'] == False:
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



