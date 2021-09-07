# -*- coding: UTF-8 -*-
# Copyright 2017-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Defines the user types for Lino Amici.

This is used as the :attr:`user_types_module
<lino.core.site.Site.user_types_module>` for Amici sites.

"""

from lino.core.roles import UserRole, SiteAdmin
from lino_xl.lib.excerpts.roles import ExcerptsUser, ExcerptsStaff
from lino_xl.lib.contacts.roles import ContactsUser, ContactsStaff
from lino_xl.lib.courses.roles import CoursesUser
from lino_xl.lib.blogs.roles import BlogsReader
from lino_xl.lib.sepa.roles import SepaStaff
from lino.modlib.office.roles import OfficeStaff, OfficeUser
from lino.modlib.checkdata.roles import CheckdataUser
from lino.modlib.about.roles import SiteSearcher
from lino_xl.lib.cal.roles import GuestOperator

from lino.modlib.comments.roles import CommentsUser, CommentsStaff
from lino_xl.lib.tickets.roles import Triager, TicketsStaff
from lino_xl.lib.votes.roles import VotesStaff, VotesUser
from lino_xl.lib.working.roles import Worker

#from lino_xl.lib.cal.roles import CalendarReader

from lino.modlib.users.choicelists import UserTypes
from django.utils.translation import gettext_lazy as _


class EndUser(OfficeUser, GuestOperator, BlogsReader, CheckdataUser):
    """An **end user** is somebody who uses our database, but won't work
    on it.

    """
    pass


class Collector(EndUser, ExcerptsUser, ContactsUser, SiteSearcher):
    """A **collector** is somebody who collects data into the database.

    """
    pass


class ProjectManager(Collector, VotesUser, Triager, CommentsUser, Worker):
    """A **project manager** additionally sees tickets, projects, courses,
    meetings, calendar...

    """
    pass


class Staff(ProjectManager, CoursesUser, ExcerptsStaff, CommentsStaff,
            VotesStaff, TicketsStaff, SepaStaff):
    pass


class SiteAdmin(Staff, SiteAdmin, OfficeStaff, ContactsStaff):
    """Can do everything."""


# class Anonymous(CommentsReader, CalendarReader):
class Anonymous(UserRole):
    pass

UserTypes.clear()
add = UserTypes.add_item
add('000', _("Anonymous"),        Anonymous, 'anonymous',
    readonly=True, authenticated=False)
add('100', _("User"),             EndUser, 'user')
add('200', _("Collector"),        Collector, 'collector')
add('300', _("Project manager"),  ProjectManager, 'manager')
add('800', _("Staff"),            Staff, 'staff')
add('900', _("Administrator"),    SiteAdmin, 'admin')
