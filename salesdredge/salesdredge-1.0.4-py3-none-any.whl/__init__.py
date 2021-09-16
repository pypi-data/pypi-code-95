from elasticsearch import Elasticsearch
from salesdredge.crawler.scraper import scrape
from salesdredge.crawler.indexer import index_pages, index_links

# SalesDredge Python Library
# API docs at ...TBD...
# Authors
# Christopher Roos <roos.christopher@gmail.com>

# Configuration variables

db_address = None
db_username = None
db_password = None
db_timeout = 30
db_indices = {
    "pages": "test_pages",
    "links": "test_links",
    "domain_links": "test_domain_links",


}

connection = Elasticsearch


def connect():
    global connection
    connection = Elasticsearch(
        [db_address],
        http_auth=(db_username, db_password),
        timeout=db_timeout)


def initialize_tables():
    for x in db_indices.keys():
        try:
            connection.indices.create(db_indices[x])
            print(db_indices[x], 'Created.')
        except Exception as e:
            print(e)

def delete_tables():
    for x in db_indices.keys():
        try:
            connection.indices.delete(db_indices[x])
            print(db_indices[x], 'Deleted.')
        except Exception as e:
            print(e)







