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

"""PyAMS_thesaurus.generations main module

This module provides site generation utility to automatically create
a thesaurus container on upgrade.
"""

from pyams_site.generations import check_required_utilities
from pyams_site.interfaces import ISiteGenerations
from pyams_thesaurus.interfaces.thesaurus import IThesaurusManager, THESAURUS_MANAGER_NAME
from pyams_utils.registry import utility_config


__docformat__ = 'restructuredtext'


REQUIRED_UTILITIES = ((IThesaurusManager, '', None, THESAURUS_MANAGER_NAME),)


@utility_config(name='PyAMS thesaurus', provides=ISiteGenerations)
class ThesaurusGenerationsChecker:
    """Thesaurus generations checker"""

    order = 100
    generation = 1

    def evolve(self, site, current=None):  # pylint: disable=unused-argument,no-self-use
        """Check for required utilities"""
        check_required_utilities(site, REQUIRED_UTILITIES)
