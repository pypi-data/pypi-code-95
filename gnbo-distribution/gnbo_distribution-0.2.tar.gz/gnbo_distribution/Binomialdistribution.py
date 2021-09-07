import math
import matplotlib.pyplot as plt
from .Generaldistribution import Distribution

class Binomial(Distribution):
    def __init__(self, prob=0.5, size=25):
        self.p=prob
        self.n=size
        Distribution.__init__(self, self.calculate_mean(), self.calculate_stdev())


    def calculate_mean(self):
        self.mean=self.p*self.n
        return self.mean
		
		
    def calculate_stdev(self):
        self.stdev=math.sqrt(self.n*self.p*(1-self.p))
        return self.stdev
		
		
    def replace_stats_with_data(self):
        data=data_list
        self.n=len(data)
        self.p=sum(data)/self.n
        self.mean=self.calculate_mean()
        self.stdev=self.calculate_stdev()
        return self.p, self.n
		
		
    def __add__(self, other):
        try:
            assert self.p == other.p, 'p values are not equal'
        except AssertionError as error:
            raise
		
        result=Binomial()
        result.n=self.n+other.n
        result.p=self.p
        result.calculate_mean()
        result.calculate_stdev()
        return result
		
		
    def __repr__(self):
        return "mean {}, standard deviation {}, p {}, n {}".format(self.mean, self.stdev, self.p, self.n)
