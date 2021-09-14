from .ncbi import esearch
from .article import Article
from .util import checkDir
import time

def datacollector_query(query, numOfresults, download=False):
    fail = []
    fail_counter = 0
    pmids = esearch(query.replace(' ', '+'), "pubmed", numOfresults)
    counter = 0
    for pmid in pmids:
        try:
            a = Article(pmid, query)
            a.fetcher()
            a.format_json()
            counter += 1
            time.sleep(1)
        except:
            pass
    
        if (download):
            try:
                a.download()
            except:
                fail.append(pmid)
                fail_counter += 1
    if fail:
        save_path = checkDir('./result/download')
        with open('{}/fail_download_{}.txt'.format(save_path, query), 'w') as out: out.write('\n'.join(fail))
    print('{} Results saved'.format(counter))
    print('{} Fail to download'.format(fail_counter))