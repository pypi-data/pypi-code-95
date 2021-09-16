# -*- coding: utf-8 -*-
#
# File: config.py
#
# Copyright (c) 2016 by Imio.be
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Andre Nuyens <andre.nuyens@imio.be>"""
__docformat__ = "plaintext"


# Product configuration.
#
# The contents of this module will be imported into __init__.py, the
# workflow configuration and every content type module.
#
# If you wish to perform custom configuration, you may put a file
# AppConfig.py in your product's root directory. The items in there
# will be included (by importing) in this file if found.

from Products.CMFCore.permissions import setDefaultRoles
from collections import OrderedDict

PROJECTNAME = "MeetingIDEA"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ("Manager", "Owner", "Contributor"))

product_globals = globals()

# Dependencies of Products to be installed by quick-installer
# override in custom configuration
DEPENDENCIES = []

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = []

from Products.PloneMeeting import config as PMconfig

IDEAROLES = {}
IDEAROLES['departmentheads'] = 'MeetingDepartmentHead'
PMconfig.MEETINGROLES.update(IDEAROLES)

PMconfig.MEETING_STATES_ACCEPTING_ITEMS = ("created", "frozen", "published", "decided")
PMconfig.MEETING_NOT_CLOSED_STATES = (
    "frozen",
    "published",
    "decided",
    "decisions_published",
)
PMconfig.EXTRA_GROUP_SUFFIXES = [
    {"fct_title": u"departmentheads", "fct_id": u"departmentheads", "fct_orgs": [], 'enabled': True}
]

from Products.PloneMeeting.model import adaptations

MIDEA_RETURN_TO_PROPOSING_GROUP_MAPPINGS = {
    "backTo_presented_from_returned_to_proposing_group": ["created"],
    "backTo_itemfrozen_from_returned_to_proposing_group": ["frozen", "decided"],
    "NO_MORE_RETURNABLE_STATES": ["closed", "archived"],
}
adaptations.RETURN_TO_PROPOSING_GROUP_MAPPINGS.update(
    MIDEA_RETURN_TO_PROPOSING_GROUP_MAPPINGS
)

IDEAMEETINGREVIEWERS = {
    "meetingitemcaidea_workflow": OrderedDict(
        [
            ("reviewers", ["proposed_to_director"]),
            ("departmentheads", ["proposed_to_departmenthead"]),
        ]
    ),
    "meetingitemcommunes_workflow": OrderedDict([('reviewers', ['proposed']),
                                                 ('prereviewers', ['proposed']), ]),
}

PMconfig.MEETINGREVIEWERS = IDEAMEETINGREVIEWERS


# import at the bottom so monkeypatches are done because PMconfig is imported in MCconfig
from Products.MeetingCommunes import config as MCconfig
