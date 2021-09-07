# Barabasi-Albert network analyser
#
# Copyright (C) 2021 Simon Dobson
#
# This file is part of epydemicarchive, a server for complex network archives.
#
# epydemicerchive is free software: you can redistribute it and/or modify
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

from collections import Counter
from scipy.optimize import curve_fit
from scipy.special import zeta
from epydemicarchive.metadata.analyser import Analyser
from epydemicarchive.metadata.degreedistribution import DegreeDistribution


class BA(DegreeDistribution):
    '''An analyser that checks for Barabasi-Albert (powerlaw) degree topology.
    Such networks have degree distrutions given by:

    .. math::

       P(k) = \frac{2m^2}{k^3}

    with exponent :meth:`k = 3` independent of :math:`m`, the number
    of edges added with each new node.

    '''

    def do(self, n, g):
        '''Compare the degree distribution of the network against
        that expected of a BA network.

        :param n: the network
        :param g: the networkx representation of the network
        :returns: a dict of metadata'''
        ba = dict()

        def model(k, m):
            return 2 * pow(m, 2) / pow(k, 3)

        N = g.order()
        degrees = [d for (_, d) in list(g.degree)]
        kmax = max(degrees)
        nks = Counter(degrees)
        pks = [nks[k] / N for k in range(kmax + 1)]
        samples = [pk for pk in pks if pk > 0]
        ks = [k for k in range(kmax + 1) if pks[k] > 0]
        (m, _) = curve_fit(model, ks, samples, jac='3-point', bounds=([0], [kmax]))
        print(m)

        return ba
