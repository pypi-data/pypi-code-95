import math
import statistics as stats

import numpy as np

from .GeneralDistribution import Distribution


class Gaussian(Distribution):
    """ Gaussian distribution class for calculating and
	visualizing a Gaussian distribution.

	Attributes:
		mean (float) representing the mean value of the distribution
		stdev (float) representing the standard deviation of the distribution
		data_list (list of floats) a list of floats extracted from the data file
	"""
    def __init__(self, mu = 0, sigma = 1):
        Distribution.__init__(self, mu, sigma)

    def __add__(self, other):
        """Magic method to add together two Gaussian distributions

        Args:
            other (Gaussian): Gaussian instance
        Returns:
            Gaussian: Gaussian distribution
        """
        result = Gaussian()
        result.mean = self.mean + other.mean
        result.stdev = np.sqrt(self.stdev ** 2 + other.stdev ** 2)

        return result

    def __repr__(self):
        """Magic method to output the characteristics of the Gaussian instance

        Args:
            None
        Returns:
            string: characteristics of the Gaussian
        """
        return f'mean {self.mean}, standard deviation {self.stdev}'

    def calculate_mean(self):
        """Method to calculate the mean of the data set.

        Args:
            None
        Returns:
            float: mean of the data set
        """
        self.mean = np.mean(self.data)
        return self.mean

    def calculate_stdev(self, sample = True):
        """Method to calculate the standard deviation of the data set.

        Args:
            sample (bool): whether the data represents a sample or population
        Returns:
            float: standard deviation of the data set
        """
        if (sample):
            # Calculate standard deviation for sample
            self.stdev = stats.stdev(self.data)
            return self.stdev
        else:
            # Calculate standard deviation for population
            self.stdev = stats.pstdev(self.data)
            return self.stdev

    def pdf(self, x):
        """Probability density function calculator for the gaussian distribution.

        Args:
            x (float): point for calculating the probability density function

        Returns:
            float: probability density function output
        """
        return (1.0 / (self.stdev * math.sqrt(2 * math.pi))) * math.exp(-0.5 * ((x - self.mean) / self.stdev) ** 2)
