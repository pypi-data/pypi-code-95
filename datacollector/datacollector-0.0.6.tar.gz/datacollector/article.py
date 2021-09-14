from metapub import PubMedFetcher
# from scidownl.scihub import *
import os
from .util import checkDir
import json
from .ncbi import getCitedby, getReferences
from .download import pdfDownload

class Article:
    def __init__(self, pmid, query):
        self.pmid = pmid
        self.query = query
    
    def fetcher(self):
        fetch = PubMedFetcher()
        article = fetch.article_by_pmid(self.pmid)
        self.article = article
        self.doi = article.doi

    def format_json(self):
        data = {}
        citedby = getCitedby(self.pmid)
        refer = getReferences(self.pmid)
        data.update({'pmid':self.pmid,
                    'authors':self.article.authors,
                    'year':self.article.year,
                    'title':self.article.title, 
                    'abstract':self.article.abstract})
        if refer: data.update(refer)
        if citedby: data.update(citedby)
        if self.query:
            save_path = checkDir('./datasets_query/json/{}'.format(self.query))
        else:
            save_path = checkDir('./datasets_id/json/{}'.format(self.query))
        with open('{}/{}.json'.format(save_path, self.pmid), 'w') as j_out:
            json.dump(data, j_out)

    def download(self):
        if not os.path.isfile("./pdf/{}.pdf".format(self.pmid)):
            pdfDownload(self.pmid, self.doi)