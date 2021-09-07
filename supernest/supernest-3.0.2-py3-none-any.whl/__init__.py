r"""Superpositional model repartitiong for accelerated nested sampling.

model repartitioning also known as posterior or more accurrately
conclusion re-partitioning is a technique that allows reshaping the
input functions: prior and likelihood and achieving faster Bayesian
inference by way of Nested Sampling.

IMPORTANT: This is an early version of the software, which does not
yet have the links to the proper publication, nor indeed is guaranteed
to function. If you use this for your research, please consider
waiting until the full release.

"""
from .core import superimpose 
from .core import gaussian_proposal 
from .core import truncated_gaussian_proposal
from .core import Proposal, NDProposal
