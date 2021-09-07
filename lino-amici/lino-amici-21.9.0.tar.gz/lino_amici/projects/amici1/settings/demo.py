# import os ; print "20161219 %s (pid:%s)" % (__name__, os.getpid())

import datetime

from ..settings import *


class Site(Site):
    is_demo_site = True
    the_demo_date = datetime.date(2019, 12, 16)
    languages = "en de fr"
    # is_demo_site = False

    # default_ui = 'lino.modlib.extjs'
    # default_ui = 'lino.modlib.bootstrap3'
    # default_user = 'anonymous'

SITE = Site(globals())
# print "20161219 b"
DEBUG = True

# the following line should not be active in a checked-in version
# DATABASES['default']['NAME'] = ':memory:'
