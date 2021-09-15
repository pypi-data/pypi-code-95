# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/


__authors__ = ["J. Garriga"]
__license__ = "MIT"
__date__ = "10/09/2019"


import unittest

import numpy

try:
    import scipy
except ImportError:
    scipy = None

from darfix.core.geneticShiftDetection import GeneticShiftDetection as GA


class TestGA(unittest.TestCase):
    """Tests for `ga.py`."""

    @classmethod
    def setUpClass(cls):

        cls.data = numpy.array([[[1, 2, 3, 4, 5],
                                 [2, 2, 3, 4, 5],
                                 [3, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5]],
                                [[1, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 3],
                                 [1, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5]],
                                [[1, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5],
                                 [8, 2, 3, 4, 5],
                                 [1, 2, 3, 4, 5]]])

        cls.optimal_shift = numpy.array([[0, 0, 0], [0, 0, 0]])
        cls.ga = GA(cls.data, cls.optimal_shift)

    def test_zero_shift_ga(self):
        """
        Tests the genetic algorithm with a given optimal_shift of 0 and no normal distribution.
        """

        self.ga.fit((0, 0), [0, 0], 10, 10)

        numpy.testing.assert_equal(self.optimal_shift, numpy.array(self.ga.support_))

    def test_initialize(self):
        """
        Tests the initialize method.
        """
        self.ga.fit((0, 0), [0, 0], 10, 10)
        population = self.ga.initialize(10)

        self.assertEqual(len(population), 10)

    def test_fitness(self):
        """
        Tests the fitness method.
        """
        self.ga.fit((0, 0), [0, 0], 10, 10)
        population = numpy.random.random((3, 2, 3))
        scores, population = self.ga.fitness(population)

        self.assertEqual(len(scores), 3)
        self.assertEqual(len(population), 3)

    def test_select(self):
        """
        Tests the select method.
        """
        self.ga.fit((0, 0), [0, 0], 10, 10)
        population = numpy.random.random((3, 2, 3))
        scores = numpy.random.random(3)
        population = self.ga.select(population, scores)

        self.assertEqual(len(population), 3)

    def test_crossover_odd(self):
        """
        Tests the crossover method when the length of the population is odd.
        """
        self.ga.fit((0, 0), [0, 0], 10, 10)
        population = numpy.random.random((3, 2, 3))
        population = self.ga.crossover(population)

        self.assertEqual(len(population), 2)

    def test_crossover_even(self):
        """
        Tests the crossover method when the length of the population is even.
        """
        self.ga.fit((0, 0), [0, 0], 10, 10)
        population = numpy.random.random((4, 2, 3))
        population = self.ga.crossover(population)

        self.assertEqual(len(population), 4)

    def test_mutate(self):
        """
        Tests the mutate method.
        """
        self.ga.fit((0, 0), [0, 0], 10, 10)
        population = numpy.random.random((3, 2, 3))
        population = self.ga.mutate(population)

        self.assertEqual(len(population), 3)

    def test_generate(self):
        """
        Tests the generate method.
        """
        self.ga.fit((0, 0), [0, 0], 10, 10)
        population = numpy.random.random((3, 2, 3))
        population = self.ga.generate(population)

        self.assertEqual(len(population), 2)

    def test_fit_best(self):
        """
        Tests correct shape of the chromosomes after fit.
        """
        self.ga.fit((0, 0), [0, 0], 10, 10)

        self.assertEqual(len(self.ga.chromosomes_best), 10)
        self.assertEqual(self.ga.support_.shape, (2, 3))

    def test_fit_scores(self):
        """
        Tests the correct lenght of the score after fit.
        """
        self.ga.fit((0, 0), [0, 0], 10, 10)

        self.assertEqual(len(self.ga.scores_best), 10)
        self.assertEqual(len(self.ga.scores_avg), 10)
