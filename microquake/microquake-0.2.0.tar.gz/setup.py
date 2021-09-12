# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['microquake',
 'microquake.clients',
 'microquake.clients.ims',
 'microquake.core',
 'microquake.core.data',
 'microquake.core.helpers',
 'microquake.core.simul',
 'microquake.core.util',
 'microquake.db',
 'microquake.db.models',
 'microquake.db.serializers',
 'microquake.imaging',
 'microquake.io.inventory',
 'microquake.io.json',
 'microquake.io.msgpack',
 'microquake.io.waveform',
 'microquake.ml',
 'microquake.pipelines',
 'microquake.plugin',
 'microquake.plugin.event',
 'microquake.plugin.grid',
 'microquake.plugin.site',
 'microquake.processors',
 'microquake.waveform']

package_data = \
{'': ['*'], 'microquake.core.data': ['resources/*']}

install_requires = \
['cachier>=1.2,<2.0',
 'dunamai>=0.8.0,<0.9.0',
 'dxfwrite>=1.2.1,<2.0.0',
 'dynaconf>=2.0,<3.0',
 'h5py>=2.10.0,<3.0.0',
 'instResp>=0.1.1,<0.2.0',
 'ipdb>=0.12.3,<0.13.0',
 'librosa>=0.7.1,<0.8.0',
 'loguru>=0.3.0,<0.4.0',
 'microquake-hashwrap>=0.0.4,<0.0.5',
 'mplstereonet>=0.5.0,<0.6.0',
 'numba>=0.48.0,<0.49.0',
 'numpy>=1.16,<2.0',
 'obspy>=1.1.1,<1.2.0',
 'pytz>=2019.1,<2020.0',
 'rq>=1.1,<2.0',
 'scipy>=1.3,<2.0',
 'sqlalchemy-utils>=0.36.1,<0.37.0',
 'tensorflow>=2.0,<3.0',
 'vtk>=8.1.2,<9.0.0',
 'walrus>=0.7.1,<0.8.0']

entry_points = \
{'console_scripts': ['MQ-autoprocess = '
                     'microquake.core.scripts.autoprocess:main',
                     'MQ-import_ESG_SEGY = '
                     'microquake.core.scripts.import_ESG_SEGY:main',
                     'MQ-init_db = microquake.core.scripts.init_db:main',
                     'MQ-init_project = '
                     'microquake.core.scripts.init_project:main',
                     'MQ-simulation = microquake.core.scripts.simulation:main',
                     'MQ-wave = microquake.ui.picker.picker:picker'],
 'microquake.io.event': ['NLLOC = microquake.io.nlloc',
                         'QUAKEML = microquake.io.quakeml'],
 'microquake.io.nlloc': ['NLLOC = microquake.io.nlloc'],
 'microquake.io.nlloc.NLLOC': ['NLLOC = microquake.io.nlloc',
                               'readFormat = '
                               'microquake.plugin.waveform:read_nlloc_hypo'],
 'microquake.io.waveform': ['ESG_SEGY = microquake.io.waveform',
                            'HSF = micorquake.io.waveform',
                            'IMS_ASCII = microquake.io.waveform',
                            'IMS_CONTINUOUS = microquake.io.waveform',
                            'TEXCEL_CSV = microquake.io.waveform'],
 'microquake.io.waveform.ESG_SEGY': ['readFormat = '
                                     'microquake.io.waveform:read_ESG_SEGY'],
 'microquake.io.waveform.HSF': ['readFormat = microquake.io.waveform:read_HSF'],
 'microquake.io.waveform.IMS_ASCII': ['readFormat = '
                                      'microquake.io.waveform:read_IMS_ASCII'],
 'microquake.io.waveform.IMS_CONTINUOUS': ['readFormat = '
                                           'microquake.io.waveform:read_IMS_CONTINUOUS'],
 'microquake.io.waveform.TEXCEL_CSV': ['readFormat = '
                                       'microquake.io.waveform:read_TEXCEL_CSV'],
 'microquake.plugin.event.NLLOC': ['readFormat = '
                                   'microquake.io.nlloc.core:read_nll_event_file'],
 'microquake.plugin.grid': ['CSV = microquake.plugin.grid',
                            'NLLOC = microquake.plugin.grid',
                            'PICKLE = microquake.plugin.grid',
                            'VTK = microquake.plugin.grid'],
 'microquake.plugin.grid.CSV': ['readFormat = microquake.plugin.grid:read_csv',
                                'writeFormat = '
                                'microquake.plugin.grid:write_csv'],
 'microquake.plugin.grid.NLLOC': ['readFormat = '
                                  'microquake.plugin.grid:read_nll',
                                  'writeFormat = '
                                  'microquake.plugin.grid:write_nll'],
 'microquake.plugin.grid.PICKLE': ['readFormat = '
                                   'microquake.plugin.grid:read_pickle',
                                   'writeFormat = '
                                   'microquake.plugin.grid:write_pickle'],
 'microquake.plugin.grid.VTK': ['writeFormat = '
                                'microquake.plugin.grid:write_vtk'],
 'microquake.plugin.site': ['CSV = microquake.plugin.site',
                            'PICKLE = microquake.plugin.site',
                            'VTK = microquake.plugin.site'],
 'microquake.plugin.site.CSV': ['readFormat = microquake.plugin.site:read_csv',
                                'writeFormat = '
                                'microquake.plugin.site:write_csv'],
 'microquake.plugin.site.PICKLE': ['readFormat = '
                                   'microquake.plugin.site:read_pickle',
                                   'writeFormat = '
                                   'microquake.plugin.site:write_pickle'],
 'microquake.plugin.site.VTK': ['writeFormat = '
                                'microquake.plugin.site:write_vtk']}

setup_kwargs = {
    'name': 'microquake',
    'version': '0.2.0',
    'description': 'Python library that is an extension/expansion/adaptation of ObsPy to microseismic data',
    'long_description': None,
    'author': 'Your Name',
    'author_email': 'you@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
