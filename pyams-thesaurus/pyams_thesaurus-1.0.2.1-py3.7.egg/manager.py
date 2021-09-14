#
# Copyright (c) 2015-2021 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_thesaurus.manager module

This module defines a thesaurus "manager", which is just a container
utility to store thesaurus.
"""

__docformat__ = 'restructuredtext'

from zope.container.folder import Folder
from zope.schema.fieldproperty import FieldProperty

from pyams_thesaurus.interfaces.thesaurus import IThesaurusManager
from pyams_utils.factory import factory_config


@factory_config(IThesaurusManager)
class ThesaurusManager(Folder):
    """Thesaurus container"""

    root_menu = FieldProperty(IThesaurusManager['root_menu'])
