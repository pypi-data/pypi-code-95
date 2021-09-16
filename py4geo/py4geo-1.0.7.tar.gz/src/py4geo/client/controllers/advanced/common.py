# -*- coding: utf-8 -*-

from ....common import db

# from py4vtile import settings as gpbfsettings
# if hasattr(gpbfsettings, "SHARE_DB") and gpbfsettings.SHARE_DB:
from py4vtile.pbfpp import common as pbfcommon
pbfcommon.db = db

from py4vtile.pbfpp import Prototizerpp as PbfPrototizer

pbfWebWrapper = PbfPrototizer()
