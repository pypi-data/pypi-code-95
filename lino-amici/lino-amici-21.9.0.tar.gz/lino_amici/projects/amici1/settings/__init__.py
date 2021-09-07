# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""The :xfile:`settings.py` modules for this variant.

.. autosummary::
   :toctree:

   demo
   fixtures

"""


from lino_amici.lib.amici.settings import *

class Site(Site):
    languages = 'en fr'
    # languages = 'en de fr et'

if False: # tim2lino usage example

    class Site(Site):
        languages = 'en de fr et'
        title = "Lino Amici"

        demo_fixtures = ['std', 'all_countries', 'tim2lino']

        legacy_data_path = '/home/luc/vbshared2/drives/L/backup/data/privat'

        def setup_plugins(self):
            super(Site, self).setup_plugins()
            self.plugins.tim2lino.configure(
                languages='et en de fr',
                dbf_table_ext = '.FOX',
                use_dbf_py=True,
                siteconfig_accounts={},
                timloader_module = 'lino_xl.lib.tim2lino.timloader_herman')
            self.plugins.checkdata.configure(responsible_user='tim')


        def get_installed_apps(self):
            yield super(Site, self).get_installed_apps()
            yield 'lino_xl.lib.tim2lino'


