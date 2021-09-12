from .general_distribution import Distribution
import numpy as np
import matplotlib.pyplot as plt


class Gaussian(Distribution):
    def __init__(self, mu=0, sigma=1):
        Distribution.__init__(self, mu, sigma)

    def calculate_mean(self):
        self.mean = np.mean(self.data)
        return self.mean

    def calculate_stdev(self, sample=True):
        if sample:
            self.stdev = np.std(self.data, ddof=1)
        else:
            self.stdev = np.std(self.data, ddof=0)
        return self.stdev

    def update_stats(self, sample=True):
        self.mean = self.calculate_mean()
        self.stdev = self.calculate_stdev(sample)

    def probability_density_fuction(self, x):
        return 1 / (self.stdev * np.sqrt(2 * np.pi)) * np.exp(-0.5 * (((x - self.mean) / self.stdev) ** 2))

    def plot_histogram_pdf(self):
        x = np.sort(np.random.normal(self.mean, self.stdev, 1000))
        y = self.probability_density_fuction(x)

        fig, ax = plt.subplots(2, sharex=True, figsize=(9, 9))
        fig.subplots_adjust(hspace=0.5)

        ax[0].hist(x, bins=100, density=True)
        ax[0].set_title('Normal Distribution Histogram\n')
        ax[0].set_ylabel('Density\n', size='large')
        ax[0].plot(x, y)

        ax[1].plot(x, y)
        ax[1].set_title('Bell Curve\n')
        ax[1].set_xlabel('\nData', size='large')
        ax[1].set_ylabel('Density\n', size='large')
        # plt.show()

    def __add__(self, other):
        result = Gaussian()
        result.mean = self.mean + other.mean
        result.stdev = np.sqrt(self.stdev ** 2 + other.stdev ** 2)
        return result

    def __repr__(self):
        return 'mean: {}, standard deviation: {}, data: {}'.format(self.mean, self.stdev, self.data)


test = Gaussian(25, 2)
print(test)
test.read_data_file('numbers.txt')
test.update_stats(sample=False)
print(test)
test.plot_histogram_pdf()
obj1 = Gaussian(5,3)
obj2 = Gaussian(10,4)
obj = obj1 + obj2
print(obj)
