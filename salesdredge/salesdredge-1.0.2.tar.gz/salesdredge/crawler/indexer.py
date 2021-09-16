from datetime import datetime
from elasticsearch.helpers import bulk


def index_documents(connection, documents, index):
    """
    Add page to the Elasticsearch Server
    :param page:
    :return:
    """

    now = datetime.now().astimezone()
    docs = []
    for doc in documents:

        doc['added'] = now.isoformat()
        doc = {
            '_index': index,
            '_id': doc['id'],
            '_source': doc,

        }
        docs.append(doc)
    bulk(connection, docs, index=index, doc_type=index, raise_on_error=True)


def index_pages(connection, documents, index):
    now = datetime.now().astimezone()
    docs = []
    for doc in documents:
        doc['added'] = now.isoformat()
        doc = {
            '_index': index,
            '_id': doc['id'],
            '_source': doc,
            "doc_as_upsert": True


        }
        docs.append(doc)
    bulk(connection, docs, index=index, doc_type=index, raise_on_error=True)

def index_links(connection, documents, index):
    now = datetime.now().astimezone()
    docs = []
    for doc in documents:
        doc['added'] = now.isoformat()
        doc = {
            '_op_type': 'create',
            '_index': index,
            '_id': doc['id'],
            '_source': doc,


        }
        docs.append(doc)
    bulk(connection, docs, index=index, doc_type=index, raise_on_error=True)
