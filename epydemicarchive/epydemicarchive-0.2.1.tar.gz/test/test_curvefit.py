# Tests for curve fitting of degree distribution
#
# Copyright (C) 2021 Simon Dobson
#
# This file is part of epydemicarchive, a server for complex network archives.
#
# epydemicarchive is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# epydemicarchive is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with epydemicarchive. If not, see <http://www.gnu.org/licenses/gpl.html>.

import unittest
from epydemic import BANetwork
from epydemicarchive.metadata.ba import BA

class TestAPI(unittest.TestCase):

    def testBA(self):
        '''Test we can fit a BA network.'''
        param = dict()
        param[BANetwork.N] = int(1e6)
        param[BANetwork.M] = 3
        g = BANetwork().set(param).generate()

        n = dict()
        ba = BA().do(n, g)


if __name__ == '__main__':
    unittest.main()
