import math

import matplotlib.pyplot as plt

from .GeneralDistribution import Distribution

class Binomial(Distribution):
    """ Binomial distribution class for calculating and
    visualizing a Binomial distribution.

    Attributes:
        - mean (float) representing the mean value of the distribution
        - stdev (float) representing the standard deviation of the distribution
        - data_list (list of floats) a list of floats to be extracted from the data file
        - p (float) representing the probability of an event occurring
    """
    # A binomial distribution is defined by two variables:
    # the probability of getting a positive outcome
    # the number of trials

    # If you know these two values, you can calculate the mean and the standard deviation
    #
    # For example, if you flip a fair coin 25 times, p = 0.5 and n = 25
    # You can then calculate the mean and standard deviation with the following formula:
    # mean = p * n
    # standard deviation = sqrt(n * p * (1 - p))

    def __init__(self, probability = .5, size = 20):
        self.p = probability
        self.n = size
        Distribution.__init__(self, self.calculate_mean(), self.calculate_stdev())

    def __add__(self, other):
        """Function to add together two Binomial distributions with equal p

        Args:
            other (Binomial): Binomial instance
        Returns:
            Binomial: Binomial distribution
        """
        try:
            assert self.p == other.p, 'p values are not equal'
        except AssertionError as error:
            raise

        result = Binomial()
        result.n = self.n + other.n
        result.p = self.p
        result.calculate_mean()
        result.calculate_stdev

        return result

    def __repr__(self):
        """Function to output the characteristics of the Binomial instance

        Args:
            None
        Returns:
            string: characteristics of the Binomial object
        """
        return f'mean {self.mean}, standard deviation {self.stdev}, p {self.p}, n {self.n}'

    def calculate_mean(self):
        """Function to calculate the mean from p and n

        Args:
            None
        Returns:
            float: mean of the data set
        """
        self.mean = self.p * self.n
        return self.mean

    def calculate_stdev(self):
        """Function to calculate the standard deviation from p and n.

        Args:
            None
        Returns:
            float: standard deviation of the data set
        """
        self.stdev = math.sqrt(self.n * self.p * (1 - self.p))
        return self.stdev

    def replace_stats_with_data(self, file_name):
        """Calculates n, p, mean and standard deviation from a data set and then
            updates the n, p, mean and stdev attributes.

        Args:
            file_name (string): name of a file to read from
        Returns:
            tuple (float, int)
                - probability of the binomial distribution
                - count of the binomial distribution data
        """
        self.read_data_file(file_name)

        self.n = len(self.data)
        self.p = self.calculate_probability()
        self.mean = self.calculate_mean()
        self.stdev = self.calculate_stdev()

        return self.p, self.n

    def calculate_probability(self):
        """Function to calculate the probability of the binomial distribuiton by
            calculationg the number of positive trials divided by the total trials.

            Args:
                None
            Returns:
                float: probability of the binomial distribution

        """
        positive_trials = 0

        for outcome in self.data:
            if outcome == 1:
                positive_trials += 1

        self.p = positive_trials / len(self.data)
        return self.p

    def plot_bar(self):
        """Function to output a histogram of the instance variable data using
            matplotlib pyplot library.

        Args:
            None
        Returns:
            None
        """
        plt.bar(x = ['0', '1'], height = [(1 - self.p) * self.n, self.p * self.n])
        plt.title('Bar Chart of Data')
        plt.xlabel('outcome')
        plt.ylabel('count')

    def pdf(self, k):
        """Probability density function calculator for the binomial distribution.

        Args:
            k (float): point for calculating the probability density function
        Returns:
            float: probability density function output
        """
        binomial_coefficient = self.calculate_binomial_coefficient(k)

        return binomial_coefficient * ((self.p) ** k) * ((1 - self.p) ** (self.n - k))

    def calculate_binomial_coefficient(self, k):
        """Calculates the  binomial coefficient associated with the input point, k

        Args:
            k (float): point for calculating the probability density function
        Returns:
            float: binomial coefficient value
        """
        return (math.factorial(self.n)) / (math.factorial(self.n - k) * math.factorial(k))

    def plot_bar_pdf(self):
        """Function to plot the pdf of the binomial distribution

        Args:
            None
        Returns:
            list: x values for the pdf plot
            list: y values for the pdf plot
        """
        x_values, y_values = []

        for number in range(self.n + 1):
            x_values.append(number)
            y_values.append(self.pdf(number))

        plt.bar(x_values, y_values)
        plt.title('Distribution of Outcomes')
        plt.xlabel('Outcome')
        plt.ylabel('Probability')
        plt.show()

        return x_values, y_values
