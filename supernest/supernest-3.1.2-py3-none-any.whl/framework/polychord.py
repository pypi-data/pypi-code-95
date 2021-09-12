"""This modules is for internal use, mostly. THis file describes the
base API that the entire framework follows. Changes here will be felt
in every single subclass of the framework, so changing things here,
should almost never alter the expected behaviour, but rather only the
internal behaviour, and handle the bugs.


If you are writing your own code, and want to make use of the sanity
checks, the somewhat less-than-elegant structure, use this file as a
last resort. For subclassing, it's much easier to look at the
subclasses in ParameterCovarianceModel. Specifically, there you shall
find the abstract base class that tells you what to do with the
likelihood, and a few examples of how to encode a prior other than
uniform.

The file itself is structured as a tutorial (more-less).
"""
from copy import deepcopy

from anesthetic import NestedSamples
from numpy import zeros

# As of now PolyChord is not `pip install pypolychord` -able
# noinspection PyUnresolvedReferences,PyUnresolvedReferences
from pypolychord import run_polychord
# noinspection PyUnresolvedReferences,PyUnresolvedReferences
from pypolychord.settings import PolyChordSettings


class Model:
    """A Base class for the models in the `super_nest` framework.

    This is what you need to sbuclass if you want to do custom stuff
    using PolyChord.

    When Sub-classing you should do three things. You need to define a
    constructor to keep the local data that you may need for
    loglikelihood and prior_quantile.

    Define the prior and the likelihood using the two unimplemented
    methods.

    """
    default_file_root = 'blankModel'

    def __init__(self, dimensionality, number_derived, file_root='', **kwargs):
        self.settings = PolyChordSettings(dimensionality, number_derived)
        self.settings.file_root = file_root

    def log_likelihood(self, theta):
        """A Ln(likelihood) of the theta given the model. With a uniform
        prior, this defines the posterior distribution up to a
        multiplicative factor.

        Parameters
        ----------
        theta : array(self.dimensionality, dtype=numpy.float64)
            Physical parameters' values.

        Returns
        -------
        logL: numpy.float64, [derived..] : list(num_derived, np.float64))

            The first element is the log-likelihood, the second is a list
            of the derived parameters.

        """
        raise NotImplementedError()

    def prior_quantile(self, hypercube):
        """Inverse Cumulative distribution function of the prior. Aka the
        quantile. If the prior has PDF \\pi, then this is (CDF (\\pi))^-1.

        Parameters
        ----------

        hypercube: array(self.dimensionality, dtype=numpy.float64)
            Physical parameters' images in a unit hypercube, where their
            distribution is uniform.

        Returns
        -------
        theta: array(self.dimensionality, dtype=numpy.float64)
            Physical parameters.
        """
        raise NotImplementedError()

    @property
    def dimensionality(self):
        """This is the length of the physical parameter vector to be used. You
        don't need to override this, unless you know what you're doing, and
        what you're doing involves passing extra dummy parameters to the
        sampler. This value is used internally for consistency checking, so
        make sure that it's correct.

        """
        return int(self.nDims)

    @property
    def num_derived(self):
        """The number of derived parameters. Override if you have derived
        parameters in self.log_likelihood.

        """
        return 0

    def test_log_like(self):
        """Not a user facing function. This is run before nested sampling is
        executed, so you should put all the sanity checking code that requires
        the self.log_likelihood here.

        """
        p = self.log_likelihood(zeros(self.dimensionality))
        try:
            _, _ = p
        except ValueError as e:
            raise ValueError(
                e.msg + "Did you forget to return the derived parameters?")

    def test_quantile(self):
        """Not a user facing function. This is run before nested sampling is
        executed, so you should put all the sanity checking code that requires
        the self.prior_quantile here.

        """
        _nDims = len(self.prior_quantile(zeros(self.dimensionality)))
        if _nDims != self.dimensionality:
            raise ValueError(
                f'Prior has the wrong dimensions: expect {_nDims}'
                f'vs actual {self.dimensionality}')

    def nested_sample(self, **kwargs):
        """A safer and more configurable way of running the `PyPolyChord`
        nested sampler.

        This will raise errors if you passed in inconsistent
        dimesnions.

        Parameters
        ----------

        **kwargs: dict
        Options that pypolychord.settings.PolyChordSettings object would accept.

        """
        self.test_log_like()
        self.test_quantile()
        _settings = self.setup_settings(**kwargs)
        output = run_polychord(self.log_likelihood, self.dimensionality,
                               self.num_derived, _settings, self.prior_quantile)
        try:
            samples = NestedSamples(
                root=f'./chains/{_settings.file_root}')
        except ValueError as e:
            print(e)
            samples = None
        return output, samples

    # noinspection SpellCheckingInspection
    def setup_settings(self, file_root=None,
                       live_points=175, resume=True, verbosity=0):
        """This is a helper function that sets PolyChord up with sane defaults.
        """
        _settings = deepcopy(self.settings)
        _settings.feedback = verbosity
        if file_root is not None:
            _settings.file_root = file_root
        _settings.read_resume = resume
        _settings.nlive = live_points
        return _settings
