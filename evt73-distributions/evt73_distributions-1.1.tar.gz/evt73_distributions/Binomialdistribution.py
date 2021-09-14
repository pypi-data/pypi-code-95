import math
import matplotlib.pyplot as plt
from .Generaldistribution import Distribution
import numpy as np
from scipy.special import comb

class Binomial(Distribution):
    """ Binomial distribution class for calculating and 
    visualizing a Binomial distribution.
    
    Attributes:
        mean (float) representing the mean value of the distribution
        stdev (float) representing the standard deviation of the distribution
        data_list (list of floats) a list of floats to be extracted from the data file
        p (float) representing the probability of an event occurring
        n (int) the total number of trials
            
    """

    def __init__(self, p=0.5, n=1):

        self.p=p
        self.n=n
        Distribution.__init__(self, self.calculate_mean(), self.calculate_stdev())

    
    def calculate_mean(self):
    
        """Function to calculate the mean from p and n
        
        Args: 
            None
        
        Returns: 
            float: mean of the data set
    
        """
        mean=(self.p)*(self.n)
        self.mean=mean

        return mean


    def calculate_stdev(self):

        """Function to calculate the standard deviation from p and n.
        
        Args: 
            None
        
        Returns: 
            float: standard deviation of the data set
    
        """
        std=math.sqrt(self.n * self.p * (1 - self.p))
        self.stdev=std
        
        return std
        
        
    def replace_stats_with_data(self):
    
        """Function to calculate p and n from the data set
        
        Args: 
            None
        
        Returns: 
            float: the p value
            float: the n value
    
        """        
        
        n_trials=len(self.data)
        probability=np.array(self.data).mean()

        self.n = n_trials
        self.p = probability
        self.calculate_mean()
        self.calculate_stdev()

        return probability, n_trials

        
    def plot_bar(self):
        """Function to output a histogram of the instance variable data using 
        matplotlib pyplot library.
        
        Args:
            None
            
        Returns:
            None
        """

        keys, counts = np.unique(self.data, return_counts=True)
        plt.title("Trials results")
        plt.xlabel("Type of elements")    
        plt.ylabel("number of appearances")
        plt.xticks(keys)
        plt.bar(keys, counts)
   
    def pdf(self, k):
        """Probability density function calculator for the gaussian distribution.
        
        Args:
            k (float): point for calculating the probability density function
            
        
        Returns:
            float: probability density function output
        """
        combinations=comb(self.n, k)
        prob_dens=combinations*((self.p)**k)*((1-self.p)**(self.n-k))
        
        return prob_dens       

    def plot_bar_pdf(self):

        """Function to plot the pdf of the binomial distribution
        
        Args:
            None
        
        Returns:
            list: x values for the pdf plot
            list: y values for the pdf plot
            
        """
        prob_for_k=[self.pdf(k) for k in range(self.n)]

        plt.title("Binomial distribution for each k")
        plt.xlabel("k(number of apperances)")
        plt.ylabel("Probability density")
        plt.bar(range(self.n), prob_for_k)

        return range(self.n), prob_for_k

                
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
                
        sum_distributions=Binomial(p=self.p, n=self.n + other.n)

        return sum_distributions        
        
    def __repr__(self):
    
        """Function to output the characteristics of the Binomial instance
        
        Args:
            None
        
        Returns:
            string: characteristics of the Gaussian
        
        """

        return 'mean {}, standard deviation {}, p {}, n {}'.format(self.mean, self.stdev, self.p, self.n)

        