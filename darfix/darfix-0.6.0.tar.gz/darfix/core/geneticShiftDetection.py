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
__date__ = "13/09/2019"


import numpy
import random

from .autofocus import normalized_variance
from .imageRegistration import apply_shift


class GeneticShiftDetection():
    """
    Class performing feature selection with a genetic algorithm.
    Selects the best shift to apply to each image from a set of images.
    Given a linear (increasing through the stack) shift that produces
    optimal results, it tries to find the best 2d normal distibution
    that, added to the optimal shift, produces the best result.

    :param array_like data: Stack of images.
    :param array_like optimal_shift: Array with 2 rows (y and x) and
        ``len(data)`` columns with an optimal linear shift.
    """
    def __init__(self, data, optimal_shift):

        assert optimal_shift.shape[1] == len(data), "Optimal shift\
        columns must be of same length as data"

        self.data = data
        self.optimal_shift = optimal_shift

    def initialize(self, size):
        """
        Initializes `size` normal distributions to be used as initial populations.

        :param int size: Size of the initial population.
        :returns: ndarray
        """
        population = []
        for i in range(size):
            normal = numpy.random.multivariate_normal(self.mean, self.sigma * numpy.eye(2), len(self.data)).T
            population.append(normal)
        return numpy.array(population)

    def fitness(self, population, shift_approach="linear"):
        """
        Finds the score of each of the individuals of a population, by means of the
        fitness function.

        :param array_like population: List of individuals to score.
        :param str shift_approach: Name of the shift approach to be used.
        :returns: ndarray, ndarray
        """

        scores = []
        for i in range(len(population)):
            result = numpy.zeros(self.data[0].shape)
            n_shift = self.optimal_shift + population[i]
            for iFrame in range(len(self.data)):
                result += apply_shift(self.data[iFrame], n_shift[:, iFrame], shift_approach)
            scores.append(normalized_variance(result))
        scores, population = numpy.array(scores), numpy.asanyarray(population)
        inds = numpy.flip(numpy.argsort(scores))
        return scores[inds], population[inds]

    def select(self, population, scores):
        """
        Selects the parents to breed the new generation. A fixed number ``self.elite_size``
        of best score population automatically becomes a parent, the others are added with
        a certain probability, which increases as the fitness score.

        :param array_like population: Population ordered by higher score.
        :param array_like score: Score, ordered from top to bottom, of each inidivual.
        """
        cum_sum = numpy.cumsum(scores) / numpy.sum(scores)
        parents = []
        elite_size = int(len(population) / 20)
        # Add the best individuals
        for i in range(elite_size):
            parents.append(population[i])
        # Chooses the rest of the parents (they can appear more than once), by
        for i in range(len(population) - elite_size):
            pick = numpy.random.random()
            for i in range(len(population)):
                if pick <= cum_sum[i]:
                    parents.append(population[i])
                    break
        return parents

    def crossover(self, parents):
        """
        Given a set of parents individuals, it randomly mixes pairs of them to create
        a new generation of children. A fixed number of parents, ``elite_size``,
        automatically becomes a child. It assumes that a first portion, bigger than
        elite_size, of parents is from the elite choosen in the select() method.

        :param array_like parents: Individuals previously chosen to become parents.
        """
        children = []
        elite_size = int(len(parents) / 100)
        for i in range(elite_size):
            children.append(parents[i])
        random.shuffle(parents)
        for i in range(int((len(parents) - elite_size) / 2)):
            for j in range(2):
                chromosome1, chromosome2 = parents[i], parents[len(parents) - 1 - i]
                child = chromosome1
                geneA = int(random.random() * len(child))
                geneB = int(random.random() * len(child))

                startGene = min(geneA, geneB)
                endGene = max(geneA, geneB)
                child[:, startGene:endGene] = chromosome2[:, startGene:endGene]
                children.append(child)
        return numpy.array(children)

    def mutate(self, children):
        """
        Given a set of children individuals, it randomly mutates some of their gens.

        :param array_like children: List of individuals.
        """
        new_population = []
        for i in range(len(children)):
            child = children[i]
            uniform = numpy.random.uniform(size=child.shape)
            normal = numpy.random.multivariate_normal(self.mean, self.sigma * numpy.eye(2),
                                                      child.shape[1]).T
            child[uniform < 0.05] += normal[uniform < 0.05]
            new_population.append(child)
        return numpy.array(new_population)

    def generate(self, population):
        """
        Creates a new generation of indidivuals.

        :param array_like population: Actual population of individuals.
        """
        # Selection, crossover and mutation
        scores_sorted, population_sorted = self.fitness(population)
        population = self.select(population_sorted, scores_sorted)
        population = self.crossover(population)
        population = self.mutate(population)
        # History
        self.chromosomes_best.append(population_sorted[0])
        self.scores_best.append(scores_sorted[0])
        self.scores_avg.append(numpy.mean(scores_sorted))

        return population

    def fit(self, mean, sigma, n_gens, size):
        """
        Computes the genetic algorithm.

        :param Union(list, tuple) mean: 2d vector to be the mean of the starting population
            of normals.
        :param number sigma: Standard deviation used to create the covariance matrix (set in
            the diagonal of 2x2 matrix).
        :param int n_gens: number of generations to compute.
        :param int size: number of individuals of the population.

        :returns: The genetic algorithm
        :rtype: GA
        """
        self.chromosomes_best = []
        self.scores_best, self.scores_avg = [], []
        self.mean = mean
        self.sigma = sigma

        population = self.initialize(size)
        for i in range(n_gens):
            population = self.generate(population)
            print("\rBest score: {:10.4f}, Avg score: {:10.4f}      {:3}%".format(self.scores_best[-1], self.scores_avg[-1],
                  int(100 * (i + 1) / n_gens)), end='\r')

        return self

    @property
    def support_(self):
        """
        Returns the best chromosome from the last iteration.
        """
        return self.chromosomes_best[-1]
