from .ncbi import esearch
from .article import Article
import time

def getNumOfresults():
    print('Enter the number of result: ')
    numOfresults = int(input())
    while(True):
        if (isinstance(numOfresults, int)): return numOfresults
        print('Please Enter the number (integer) of result: ')
        numOfresults = int(input())

def getQuery():
    print('Enter search query: ')
    query = input()
    while(True):
        if query: return query
        print('Please Enter non-empty search query: ')
        query = input()

def getIsDownload():
    print("Download? (y/n) ")
    isDownload = input()
    while(True):
        if isDownload.lower() == 'y': return True
        if isDownload.lower() == 'n': return False
        print('Please Enter either "y" as Yes or "n" as No.')
        print("Download? (y/n) ")
        isDownload = input()

def getFormatType():
    format_type = ['json', 'xml', 'csv']
    print('Save Format (JSON / XML / CSV): ')
    format = input()
    while(True):
        if format.lower() in format_type: return format
        print("We don't have this type ({}) format. Please Enter Again.".format(format))
        print('Save Format (JSON / XML / CSV): ')
        format = input()

def ui():
    query = getQuery()
    numOfresults = getNumOfresults()
    # format = getFormatType()
    isDownload = getIsDownload()
    # print('Query: {}\t\tNumber of result: {}\t\tSave Format: {}\t\tDownload? {}'.format(query, numOfresults, format.upper(), isDownload))
    print('Query: {}\t\tNumber of result: {}\t\tDownload? {}'.format(query, numOfresults, isDownload))
    return query, numOfresults ,isDownload #, format

if __name__ == "__main__":
    fail = []
    fail_counter = 0
    query, numOfresults, isDownload = ui()
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
    
        if (isDownload):
            try:
                a.download()
            except:
                fail.append(pmid)
                fail_counter += 1
        if fail:
            with open('fail_download.txt', 'w') as out: out.write('\n'.join(fail))
    print('{} Results saved'.format(counter))
    print('{} Fail to download'.format(fail_counter))