import math
from os import supports_effective_ids
import matplotlib.pyplot as plt
from .Generaldistribution import Distribution
from seaborn import boxplot
import numpy as np

class Gaussian(Distribution):
	""" Gaussian distribution class for calculating and 
	visualizing a Gaussian distribution.
	
	Attributes:
		mean (float) representing the mean value of the distribution
		stdev (float) representing the standard deviation of the distribution
		data_list (list of floats) a list of floats extracted from the data file
			
	"""
	def __init__(self, mu=0, sigma=1):
		
		Distribution.__init__(self, mu, sigma)
	
		
	
	def calculate_mean(self):
	
		"""Function to calculate the mean of the data set.
		
		Args: 
			None
		
		Returns: 
			float: mean of the data set
	
		"""
		mean=np.array(self.data).mean()
		self.mean=mean

		return mean


	def calculate_stdev(self, sample=True):

		"""Function to calculate the standard deviation of the data set.
		
		Args: 
			sample (bool): whether the data represents a sample or population
		
		Returns: 
			float: standard deviation of the data set
	
		"""

		if sample==True:

			std=np.array(self.data).std()
			std=std**2
			std=std*(len(self.data))/(len(self.data) - 1)
			std=math.sqrt(std)
			self.stdev=std

			return std

		else:

			std=np.array(self.data).std()
			self.stdev=std	

			return std	
		
		
	def plot_histogram(self):
		"""Function to output a histogram of the instance variable data using 
		matplotlib pyplot library.
		
		Args:
			None
			
		Returns:
			None
		"""
		plt.hist(self.data)
		plt.title('Histogram of Data')
		plt.xlabel('data')
		plt.ylabel('count')
		
		
		
	def pdf(self, x):
		"""Probability density function calculator for the gaussian distribution.
		
		Args:
			x (float): point for calculating the probability density function
			
		
		Returns:
			float: probability density function output
		"""
		mu=self.mean
		sigma= self.stdev

		power_of_e=((x-mu)**2)/(2.00*(sigma**2))
		norm_coef=1.000/((2*(np.pi)*(sigma**2))**0.5)
		prob_density=norm_coef*((np.e)**(-1*power_of_e))
		
		return prob_density


	
	def replace_stats_with_data(self):
		''' replace mean and std given a data of my object

		Args:
			None
		Returns:
			None
		
		'''

		self.calculate_mean()
		self.calculate_stdev()		

	def plot_histogram_pdf(self, n_spaces = 50):

		"""Function to plot the normalized histogram of the data and a plot of the 
		probability density function along the same range
		
		Args:
			n_spaces (int): number of data points 
		
		Returns:
			list: x values for the pdf plot
			list: y values for the pdf plot
			
		"""
		
		mu = self.mean
		sigma = self.stdev

		min_range = min(self.data)
		max_range = max(self.data)
		
		 # calculates the interval between x values
		interval = 1.0 * (max_range - min_range) / n_spaces

		x = []
		y = []
		
		# calculate the x values to visualize
		for i in range(n_spaces):
			tmp = min_range + interval*i
			x.append(tmp)
			y.append(self.pdf(tmp))

		# make the plots
		fig, axes = plt.subplots(2,sharex=True)
		fig.subplots_adjust(hspace=.5)
		axes[0].hist(self.data, density=True)
		axes[0].set_title('Normed Histogram of Data')
		axes[0].set_ylabel('Density')

		axes[1].plot(x, y)
		axes[1].set_title('Normal Distribution for \n Sample Mean and Sample Standard Deviation')
		axes[0].set_ylabel('Density')
		plt.show()

		return x, y
		
	def __add__(self, other):
		
		"""Function to add together two Gaussian distributions
		
		Args:
			other (Gaussian): Gaussian instance
			
		Returns:
			Gaussian: Gaussian distribution
			
		"""
		
		result = Gaussian()
		result.mean = self.mean + other.mean
		result.stdev = math.sqrt(self.stdev ** 2 + other.stdev ** 2)
		
		return result
		
		
	def __repr__(self):
	
		"""Function to output the characteristics of the Gaussian instance
		
		Args:
			None
		
		Returns:
			string: characteristics of the Gaussian
		
		"""
		
		return "mean {}, standard deviation {}".format(self.mean, self.stdev)


	def plot_boxplot(self):
		""" Box plot of the data 

		Args:
			None
		Returns:
			None
		
		"""

		fig, ax=plt.subplots()
		ax.set_title('Box Plot of data')
		boxplot(self.data, ax=ax)

		return fig
	
	def CDF(self, x):
		'''Cumulative Distribution Function
		
		Args:
			x, point to be calculated
			mean, mean of a Gaussian function
			std, standard deviation of a Gaussian Function
		Return:
			elements below x
		'''
		return (0.5)*((1+math.erf(x-self.mean))/((self.stdev)*(math.sqrt(2))))

