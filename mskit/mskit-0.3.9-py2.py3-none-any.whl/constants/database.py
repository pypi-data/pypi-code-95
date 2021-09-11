"""
ProteomeXchange
    Pride

"""


class ProteomeXchange:
    PXD_Dataset = 'http://proteomecentral.proteomexchange.org/cgi/GetDataset?ID={}'

    class Pride:
        """
        https://pride-archive.github.io/PrideAPIDocs/hyperlinks.html

        ListQueryUrl:
            Url + Project ID (PXD...)
                e.g. https://www.ebi.ac.uk/pride/ws/archive/file/list/project/PXD004732
            This will get a json file
        Example FTP file address
            ftp://ftp.pride.ebi.ac.uk/pride/data/archive/2018/06/PXD009449/MaxQuant_1.5.3.30.zip
        Example https file address
            https://ftp.pride.ebi.ac.uk/pride/data/archive/2019/07/PXD008355/txt.zip

        """
        ListQueryUrl = 'https://www.ebi.ac.uk/pride/ws/archive/file/list/project/'
        FTP_Url = 'ftp://ftp.pride.ebi.ac.uk'
        ASP_Url = 'era-fasp@fasp.pride.ebi.ac.uk:'
        FTP_IP = '193.62.197.74'
        HTTPS_Url = 'https://ftp.pride.ebi.ac.uk'

        PRIDE_StoragePrefix = '/pride/data/archive/'


    class Massive:
        FTP_Url = 'ftp://massive.ucsd.edu'
        FTP_IP = '132.249.211.16'

    class JPOST:
        FTP_Url = 'ftp://ftp.biosciencedbc.jp'
        StoragePrefix = '/archive/jpostrepos/'
        FTP_IP = '160.74.86.87'

        ProjectInfo = 'https://repository.jpostdb.org/entry/{}'  # JPST000859
        ProjectXML = 'https://repository.jpostdb.org/xml/{}.{}.xml'  # JPST000859, 3
        SingleFileUrl = 'https://repository.jpostdb.org/data/{}.{}/{}'  # JPST000859, 3, FileName


class DGI:
    """
    Drug Gene Interaction: http://www.dgidb.org/
    """
    DGIInteractionURL = r'http://dgidb.org/api/v2/interactions.json?genes={}'


class KEGG:
    KEGGDrugDatabaseFind = r'http://rest.kegg.jp/find/drug/{}'  # Fill in drug name which is connected with plus sign
    KEGGGetURL = r'http://rest.kegg.jp/get/{}'  # Fill in drug D number


class STRING:
    STRING_API_URL = "https://string-db.org/api"
    Methods = ['interaction_partners']
    OutputFormat = []


class Uniprot:
    MainUrl = 'https://www.uniprot.org/'
