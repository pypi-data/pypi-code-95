"""This is an object-oriented interface to proposals and PolyChord.

The intent is to ease exploration of models with plain PolyChord (and
anesthetic). This is here to help propototype the types of proposals,
likelihood functions and calibrate the Bayesian inference.

This is less helpful in cases where you want to adjust a project
that's already using Bayesian inference. For the purposes of **just**
using superpositional mixtures, refer to `super_nest.superimpose()`.

Most of the prototyping is usually done with a lightweight likelihood
function that's ordinarily well-approximated by a Gaussian (or a sum
of gaussians). For this purpose see the submodule

`gaussian_models`

If you need to write custom code, the functions in the same module
provide a good example of how to subclass the Model, and therefore
adapt the interface to your workflow.
"""
from .polychord import Model
