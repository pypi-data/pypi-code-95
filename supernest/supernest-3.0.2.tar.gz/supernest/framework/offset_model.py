"""This classs provides a convenient wrapper around the standard
models, and allows introducing an offset between the likelihood and
prior coordinate systems. This is useful for testing and simulating
priors that have are at variance with the likelihood. You only need
this, if you want to have a prior that\'s **deliberately** offset from
where you expect the likelihood peak to be located at.

"""
from numpy import pad

from .polychord import Model


class OffsetModel(Model):
    """An abstract offset model decorator. Pass it any model and it will
    return a model that's offset by a vector.

    """
    default_file_root = 'OffsetModel'

    def __str__(self):
        return f'{self.model.__str__()}\nOffset by {self.offset}'

    def __repr__(self):
        return f'{self.model.__repr__()} Offset by {self.offset}'

    def __init__(self, base_model, offset, file_root=default_file_root, **kwargs):
        self.model = base_model
        self.offset = offset
        if not self.offset.size == self.model.dimensionality:
            self.offset = pad(self.offset, (0, abs(
                self.model.dimensionality - self.offset.size)))
        super().__init__(base_model.dimensionality,
                         base_model.num_derived, file_root=file_root, **kwargs)

    def log_likelihood(self, theta):
        return self.model.log_likelihood(theta - self.offset)

    def prior_quantile(self, *args):
        return self.model.prior_quantile(*args)

    @property
    def dimensionality(self):
        return self.model.dimensionality
