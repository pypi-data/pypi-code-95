import re
import logging 

import rdflib
import rdflib.__init__ as rdflib_init__

from pkg_resources import get_distribution

from validator_collection import checkers, errors

from rdflib import URIRef
from rdflib import namespace 
from rdflib.namespace import Namespace, ClosedNamespace

from rdflib import DCTERMS,DOAP
from rdflib import SDO

__version__ = get_distribution("ejerico-harvester").version

__ADMS = Namespace("http://www.w3.org/ns/adms#")
__BODC = Namespace("http://vocab.nerc.ac.uk/collection/")
__DIRECT = Namespace("http://www.direct-mapping.org/ns#")
__EJERICO = Namespace("http://www.ejerico.org/ns#")
__EPOS = Namespace("https://www.epos-eu.org/epos-dcat-ap#")
__HTTP = Namespace("http://www.w3.org/2011/http#")
__HYDRA = Namespace("http://www.w3.org/ns/hydra/core#")
__LOCN = Namespace("http://www.w3.org/ns/locn#")
__SOCIB = Namespace("http://www.socib.es/ns#")
__SPDX = Namespace("http://spdx.org/rdf/terms#")
__VCARD = Namespace("https://www.w3.org/2006/vcard/ns#")

rdflib_init__.__all__.append("ADMS")
setattr(rdflib,"ADMS",__ADMS)

rdflib_init__.__all__.append("BODC")
setattr(rdflib,"BODC",__BODC)

rdflib_init__.__all__.append("EJERICO")
setattr(rdflib,"DIRECT",__DIRECT)

rdflib_init__.__all__.append("EJERICO")
setattr(rdflib,"EJERICO",__EJERICO)

rdflib_init__.__all__.append("EPOS")
setattr(rdflib,"EPOS",__EPOS)

rdflib_init__.__all__.append("HTTP")
setattr(rdflib,"HTTP",__HTTP)

rdflib_init__.__all__.append("HYDRA")
setattr(rdflib,"HYDRA",__HYDRA)

rdflib_init__.__all__.append("LOCN")
setattr(rdflib,"LOCN",__LOCN)

rdflib_init__.__all__.append("SOCIB")
setattr(rdflib,"SOCIB",__SOCIB)

rdflib_init__.__all__.append("SPDX")
setattr(rdflib,"SPDX",__SPDX)

rdflib_init__.__all__.append("DCT")
setattr(rdflib,"DCT",DCTERMS)

rdflib_init__.__all__.append("SCHEMA")
setattr(rdflib,"SCHEMA",SDO)

rdflib_init__.__all__.append("VCARD")
setattr(rdflib,"VCARD",__VCARD)

checkers.is_sha1 = lambda x: re.match(r"\b[0-9a-f]{40}\b")
