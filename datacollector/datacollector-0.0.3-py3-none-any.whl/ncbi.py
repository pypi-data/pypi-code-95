from metapub import PubMedFetcher
import xml.etree.ElementTree as ET
import urllib.request
from socket import timeout

# To create an url to use the NCBI API
def createURL(functionID, termORmids, db, numOfresults):
    entrezURL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    function = ["esearch.fcgi?db=", "efetch.fcgi?db="]      # 0:Search for MIDs, 1:Fetch for Articles
    function2 = ["&term=", "&id="]
    urlType = '&rettype=xml'
    max = '&retmax=' + str(numOfresults)  # max number of id you want, max number is between 440 - 445 because of the sine of the url
    start = '&retstart=0'
    api_key = '&api_key=0da8d9d247316e94097c6614783b2190db08'
    url = entrezURL + function[functionID] + db + function2[functionID] + termORmids + urlType + start + max + api_key
    # print(url)
    return url

# To get the xml from db
def getXML(url):
    try:
        data = urllib.request.urlopen(url).read()
    except ConnectionResetError:
        print("==> ConnectionResetError")
        print(url)
        pass
    except timeout: 
        print("==> Timeout")
        print(url)
        pass
    tree = ET.fromstring(data)
    return tree

# To get the MIDs
def esearch(keyword, db, numOfresults):
    keyword = keyword.replace(' ', '+').replace('"', '')
    url = createURL(0, keyword + '[title]', db, numOfresults)
    tree = getXML(url)
    mids = []
    for id in tree.findall('.//Id'):
        mids.append(id.text)
    return mids

def getCitedby(pmid):
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&linkname=pubmed_pubmed_citedin&id={}&api_key=0da8d9d247316e94097c6614783b2190db08'
    root = getXML(url.format(pmid))
    # print(url.format(pmid))
    citedby = root.findall('.//Link/Id')
    if not citedby: return []
    id_list = { "citedby" : [] }
    if citedby:
        for id in citedby:
            if id is not None:
                id_list['citedby'].append(int(id.text))
    return id_list

def getReferences(pmid):
    url = createURL(1, pmid, 'pubmed', 1)
    root = getXML(url)
    # print(url)
    referID_list = root.findall('.//ReferenceList/Reference/ArticleIdList/ArticleId[@IdType="pubmed"]')
    if not referID_list: return []
    referList = { "references" : [] }
    for referenceId in referID_list:
        referList["references"].append(int(referenceId.text))
    return referList