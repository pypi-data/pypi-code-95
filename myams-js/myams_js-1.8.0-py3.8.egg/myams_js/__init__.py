#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""MyAMS.js package

MyAMS.js extension framework
"""

import os

from fanstatic import Library, Resource, Group
from pkg_resources import Requirement, resource_filename

from pyams_utils.fanstatic import ResourceWithData


__docformat__ = 'restructuredtext'


pkg_dir = resource_filename(Requirement.parse('myams_js'), 'pkg')
if not os.path.exists(pkg_dir):
    pkg_dir = '../../pkg'  # fallback for source installation

library = Library('myams', pkg_dir)


#
# MyAMS external resources
#

jquery = Resource(library, 'js/ext/jquery.js',
                  minified='js/ext/jquery.min.js')

jsrender = Resource(library, 'js/ext/jsrender.js',
                    minified='js/ext/jsrender.min.js',
                    depends=(jquery,))

bootstrap_css = Resource(library, 'css/ext/bootstrap.css',
                         minified='css/ext/bootstrap.min.css')

bootstrap = Resource(library, 'js/ext/bootstrap.js',
                     minified='js/ext/bootstrap.min.js',
                     depends=(jquery,))

fontawesome_css = Resource(library, 'css/ext/fontawesome.css',
                           minified='css/ext/fontawesome.min.css',
                           depends=(bootstrap_css,))

fontawesome_js = ResourceWithData(library, 'js/ext/fontawesome.js',
                                  minified='js/ext/fontawesome.min.js',
                                  data={
                                      'auto-replace-svg': 'nest',
                                      'search-pseudo-elements': ''
                                  })


#
# MyAMS bundles
#

myams_full_bundle = ResourceWithData(library, 'js/dev/myams-dev.js',
                                     minified='js/prod/myams.js')

myams_css = Resource(library, 'css/dev/myams.css',
                     minified='css/prod/myams.css')

myams_mini_js = Resource(library, 'js/dev/myams-mini-dev.js',
                         minified='js/prod/myams-mini.js',
                         depends=(jquery, bootstrap))

myams_mini_bundle = Group(depends=(fontawesome_css, myams_css, myams_mini_js))

myams_mini_svg_bundle = Group(depends=(fontawesome_js, myams_css, myams_mini_js))

myams_core_js = Resource(library, 'js/dev/myams-core-dev.js',
                         minified='js/prod/myams-core.js',
                         depends=(jquery, jsrender, bootstrap))

myams_core_bundle = Group(depends=(fontawesome_css, myams_css, myams_core_js))

myams_core_svg_bundle = Group(depends=(fontawesome_js, myams_css, myams_core_js))


emerald_css = Resource(library, 'css/dev/emerald.css',
                       minified='css/prod/emerald.css')

emerald_mini_bundle = Group(depends=(fontawesome_css, emerald_css, myams_mini_js))

emerald_mini_svg_bundle = Group(depends=(fontawesome_js, emerald_css, myams_mini_js))

emerald_core_bundle = Group(depends=(fontawesome_css, emerald_css, myams_core_js))

emerald_core_svg_bundle = Group(depends=(fontawesome_js, emerald_css, myams_core_js))
