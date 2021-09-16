# -*- coding: utf-8 -*-
# pylint: disable=W0622
# copyright 2017-2021 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


"""cubicweb-saml application packaging information"""


modname = 'cubicweb_saml'
distname = 'cubicweb-saml'

numversion = (0, 4, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = 'SAML2 authentifier'
web = 'https://forge.extranet.logilab.fr/cubicweb/cubes/%s' % distname

__depends__ = {
    'cubicweb': ">= 3.30.0",
    'logilab-common': '>= 1.4.0',
    'pyramid': '>= 1.10.4',
    'pysaml2': '>= 5.0.0',
    'requests': '>= 2.22.0',
    'zope.interface': '>= 4.1.2',
}
__recommends__ = {}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
]
