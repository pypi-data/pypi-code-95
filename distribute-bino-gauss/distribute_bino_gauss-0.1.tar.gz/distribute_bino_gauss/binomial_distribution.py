import numpy as np
from .general_distribution import Distribution
import matplotlib.pyplot as plt
from scipy.special import factorial


class Binomial(Distribution):
    def __init__(self, prob=0.5, size=10):
        self.n = size
        self.p = prob
        Distribution.__init__(self, self.calculate_mean(), self.calculate_stdev())

    def calculate_mean(self):
        self.mean = self.n * self.p
        return self.mean

    def calculate_stdev(self):
        self.stdev = np.sqrt(self.n * self.p * (1 - self.p))
        return self.stdev

    def update_stats(self):
        self.n = len(self.data)
        self.p = sum(self.data) / len(self.data)
        self.mean = self.calculate_mean()
        self.stdev = self.calculate_stdev()

    def probability_density_func(self, k):
        comb = factorial(self.n) / (factorial(k) * (factorial(self.n - k)))
        p = comb * self.p ** k * (1 - self.p) ** (self.n - k)
        return p

    def plot_bar_pdf(self):
        fig, ax = plt.subplots(2)
        fig.subplots_adjust(hspace=0.5)

        ax[0].bar(['0', '1'], [len(self.data) - sum(self.data), sum(self.data)], width=0.25)
        ax[0].set_title('bar chart of data')
        ax[0].set_xlabel('data', size='large')
        ax[0].set_ylabel('count', size='large')
        ax[0].set_yticks(np.arange(len(self.data)))

        x = np.arange(self.n + 1)
        y = self.probability_density_func(x)

        ax[1].bar(x, y, width=0.25)
        ax[1].plot(x, y, 'red')
        ax[1].set_title('binomial distribution of data')
        ax[1].set_xlabel('k')
        ax[1].set_ylabel('p')
        ax[1].set_xticks(x)

        plt.show()

    def __add__(self, other):
        result = Binomial()
        result.n = self.n + other.n
        result.p = self.p
        result.mean = result.calculate_mean()
        result.stdev = result.calculate_stdev()
        return result

    def __repr__(self):
        return 'n: {}, p: {}, mean: {}, standard deviation: {}, data: {}'.format(self.n, self.p, self.mean,
                                                                                 self.stdev, self.data)


test = Binomial(0.25, 20)
print(test)
test.read_data_file('numbers_binomial.txt')
test.update_stats()
print(test)
test.plot_bar_pdf()
print()
obj1 = Binomial(0.25, 20)
obj2 = Binomial(0.25, 10)
obj = obj1 + obj2
print(obj)


