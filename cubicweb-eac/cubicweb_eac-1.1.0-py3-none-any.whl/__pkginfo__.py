# pylint: disable=W0622
"""cubicweb-eac application packaging information"""

distname = "cubicweb-eac"
modname = "cubicweb_eac"  # required by apycot

numversion = (1, 1, 0)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "LOGILAB S.A. (Paris, FRANCE)"
author_email = "contact@logilab.fr"
description = "Implementation of Encoded Archival Context for CubicWeb"
web = "https://forge.extranet.logilab.fr/cubicweb/cubes/%s" % distname

__depends__ = {
    "cubicweb": ">= 3.26.0, < 3.34.0",
    "cubicweb-prov": ">= 0.4.0",
    "cubicweb-skos": ">= 1.3.0",
    "cubicweb-addressbook": ">=1.6.0",  # first release with python3 support
    "cubicweb-compound": ">= 0.6.0",
    "python-dateutil": None,
}
__recommends__ = {}

classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: JavaScript",
]
