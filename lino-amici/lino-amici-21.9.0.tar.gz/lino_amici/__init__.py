# -*- coding: UTF-8 -*-
# Copyright 2014-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""This is the main module of Lino Amici.

.. autosummary::
   :toctree:

   lib


"""

from .setup_info import SETUP_INFO

__version__ = SETUP_INFO['version']

intersphinx_urls = dict(docs="https://lino-framework.gitlab.io/amici/")
srcref_url = 'https://gitlab.com/lino-framework/amici/blob/master/%s'
doc_trees = ['docs']
