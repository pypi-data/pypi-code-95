import torch

class Likelihood:
    def forward(self, x):
        raise NotImplementedError()

class GaussianLikelihood(Likelihood):
    def __init__(self, var=1.0):
        pass

    def forward(self, x):
        return torch.distributions.normal.Normal()
