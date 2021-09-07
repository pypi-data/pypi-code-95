# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Some demo data for the Vilma project.

"""

from lino.api import dd, rt, _
from lino.utils.mldbc import babel_named as named
from lino.utils.cycler import Cycler
from lino_xl.lib.cal.choicelists import Recurrencies

def objects():
    Topic = rt.models.topics.Topic
    EventType = rt.models.cal.EventType
    Room = rt.models.cal.Room
    Company = rt.models.contacts.Company
    Person = rt.models.contacts.Person
    Role = rt.models.contacts.Role
    RoleType = rt.models.contacts.RoleType

    school = named(Room, _("School"))
    yield school
    center = named(Room, _("Youth center"))
    yield center
    library = named(Room, _("Library"))
    yield library
    
    training = named(EventType, _("Training"))
    yield training
    workshop = named(EventType, _("Travel"))
    yield workshop
    camp = named(EventType, _("Camp"))
    yield camp
    
    nature = named(Topic, _("Nature"))
    yield nature
    folk = named(Topic, _("Folk"))
    yield folk
    health = named(Topic, _("Health"))
    yield health
    comp = named(Topic, _("Computer"))
    yield comp
    
