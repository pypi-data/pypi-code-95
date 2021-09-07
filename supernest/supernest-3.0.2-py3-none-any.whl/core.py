r"""Module containing superimpose and a gaussian proposal.

The usage is as follows. Normally the proposal is approximated by a
correlated Gaussian distribution. We (for now) approximate that
further to a spherically symmetric gaussian and use that as the guide
for nested sampling.

Afterwards, the important step is to put the Gaussian proposal into a
superpositional mixture.  This is done via a functional interface for
ease and portability.

"""
from random import random, seed
from numpy import concatenate, sqrt, log, pi, array, ndarray, zeros, isclose
from numpy.linalg import inv as minverse
from numpy.linalg import slogdet
import numpy.linalg
from scipy.special import erf, erfinv
from collections import namedtuple
import warnings

Proposal = namedtuple("Proposal", ['prior', 'likelihood'])
NDProposal = namedtuple("NDProposal", ['nDims', 'prior', 'likelihood'])

debug = False


def superimpose(models: list, nDims: int = None):
    r"""Superimpose functions for use in nested sampling packages.

    Parameters
    ----------
    models: list(tuples(callable, callable))

    This is a list of pairs of functions. The first functions
    (quantile-like) will be interpreted as prior quantiles. They will
    be made to accept extra arguments from the hypercube, and produce
    extra parameters as output.

    The secondary function will be made to accept extra parameters,
    and ignore all but the last parameter. The functions need to be a
    consistent partitioning of the model, as described in the
    stochastic superpositional mixing paper in mnras.

    In short, if the prior spaces to which the two functions coorepond
    is the same, for all functions, you only need to make sure that
    the product of the prior pdf and the likelihood pdf is the same
    acroos different elemtns of the tuple. If they are not the same,
    you must make sure that the integral of their product over each
    prior space is the same, and that the points which correspond to
    the same locations in the hypercube align.

    nDims=None: int
    Optionally, if you want to have `superimpose`
    produce a number of dimensions for use with e.g. PolyChord, and to
    guard againt changes in the calling conventions and API, just pass
    the nDims that you would pass to PolyChord.Settings, and the
    run_polychord function.


    Returns
    -------
    (prior_quantile: callable, likelihood: callable) : tuple
    if nDims is None,
    returns a tuple of functions: the superposition of the prior
    quantiles and the likelihoods (in that order).

    (nDims: int, prior_quantile: callable, likelihood: callable): tuple
    if the optional argument nDims is not None, the output also
    contains an nDims: the number of dimensions that you should ask
    your dimesnional sampler to pass.

    """
    priors, likes = [p for p, _ in models], [l for _, l in models]

    def prior_quantile(cube):
        physical_params = cube[:-len(models)]
        choice_params = cube[-len(models):-1]
        index = 0
        norm = choice_params.sum()
        norm = 1 if norm == 0 or len(choice_params) == 1 else norm
        probs = choice_params / norm
        h = hash(tuple(physical_params))
        seed(h)
        rand = random()
        for p in probs:
            if rand > p:
                break
            index += 1
        theta = priors[index](physical_params)
        ret = array(concatenate([theta, probs, [index]]))
        return ret

    def likelihood(theta):
        try:
            physical_params = theta[:-len(models)]
        except SystemError:
            warnings.warn(f'theta = {theta} {theta[:-len(models)]}')
            physical_params = theta[:-len(models)]
        index = int(theta[-1:].item())
        ret = likes[index](physical_params)
        return ret

    if nDims is not None:
        return NDProposal(nDims + len(models), prior_quantile, likelihood)
    else:
        return Proposal(prior_quantile, likelihood)


def _eitheriter(ab):
    a, b = ab
    return hasattr(a, '__iter__') or hasattr(b, '__iterb__')


def __snap_to_edges(cube, theta, a, b):
    # TODO use cython for efficient indexing.
    ret = theta
    if not hasattr(a, '__iter__'):
        a = a + zeros(len(theta))
    if not hasattr(b, '__iter__'):
        b = b + zeros(len(theta))
    for i in range(len(cube)):
        if isclose(cube[i], 0):
            ret[i] = a[i]
        elif isclose(cube[i], 1):
            ret[i] = b[i]
        else:
            pass
    return ret


def gaussian_proposal(bounds: ndarray,
                      mean: ndarray,
                      covmat: ndarray,
                      loglike: callable = None):
    r"""Produce a Gaussian proposal.

    Given a uniform prior defined by bounds, produces the corrected
    loglikelihood and prior.

    Parameters
    ----------
    bounds: array-like
        A tuple-like or array-like that contains the (min, max) of the
        original uniform prior.

    mean: array-like
        A vector of the means of the gaussian approximation of the proposal

    covmat: array-like
        A matrix containing the covariance of the gaussian proposal.

    loglike: callable (optional)
        The loglikelihood function of the original model to be corrected.

    Returns
    -------
    proposal: Proposal (tuple(prior, loglike))
    """
    covmat, a, b = _process_stdev(covmat, mean, bounds)
    log_box = log(b - a).sum() if _eitheriter(
        (a, b)) else len(mean) * log(b - a)
    log_box = -log_box
    try:
        invCov = minverse(covmat)
    except numpy.linalg.LinAlgError:
        invCov = 1/covmat

    def __quantile(cube):
        theta = sqrt(2) * erfinv(2*cube - 1)
        theta = mean + covmat @ theta
        return theta

    def __correction(theta):
        if loglike is None:
            ll, phi = 0, []
        else:
            ll, phi = loglike(theta)
        corr = - numpy.linalg.multi_dot([(theta - mean), invCov,
                                         (theta - mean)])/2
        corr -= log(2 * pi)*len(mean)/2 + slogdet(covmat)[1] / 2
        if debug:
            print(f'll={ll}\t corr={corr}')
        return (ll - corr + log_box), phi

    return Proposal(__quantile, __correction)


def truncated_gaussian_proposal(bounds: ndarray,
                                mean: ndarray,
                                stdev: ndarray,
                                loglike: callable = None):
    r"""Produce a truncated Gaussian proposal.

    Given a uniform prior defined by bounds, it produces a gaussian
    prior quantile and a correction to the log-likelihood.

    Parameters
    ----------
    bounds : array-like
        A tuple with bounds of the original uniform prior.

    mean : array-like
        The vector \mu at which the proposal is to be centered.

    stdev : array-like
        The vector of standard deviations. Currently only
        uncorrelated Gaussians are supported.

    loglike: callable: (array-like) -> (real, array-like), optional
        The callable that constitutes the model likelihood.  If provided
        will be included in the output. Otherwise assumed to be
        lambda () -> 0


    Returns
    -------
    (prior_quantile, loglike_corrected): tuple(callable, callable)
    This is the output to be used in the stochastic mixing. You can
    use it directly, if you\'re certain that this is the exact shape of
    the posterior. Any deviation, however, will be strongly imprinted
    in the posterior, so you should think carefully before doing this.

    """
    stdev, a, b = _process_stdev(stdev, mean, bounds)
    # truncation requires the covmat to be diagonal
    try:
        stdev = stdev.diagonal()
    except ValueError:
        warnings.warn(f'stdev={stdev} couldn\'t be diagonalised')
    log_box = log(b - a).sum() if _eitheriter(
        (a, b)) else len(mean) * log(b - a)
    log_box = -log_box

    # Convenice variable to avoid duplicating code
    RT2, RTG = sqrt(2), sqrt(1 / 2) / stdev
    da = erf((a - mean) * RTG)
    db = erf((b - mean) * RTG)

    def __quantile(cube):
        theta = RT2 * erfinv((1 - cube) * da + cube * db)
        theta = mean + stdev * theta
        theta = __snap_to_edges(cube, theta, a, b)
        return theta

    def __correction(theta):
        if loglike is None:
            ll, phi = 0, []
        else:
            ll, phi = loglike(theta)
        corr = -((theta - mean)**2) / (2 * stdev)
        corr -= log(2 * pi * stdev**2) / 2
        corr -= log((db - da) / 2)
        corr = corr.sum()
        if debug:
            print(f'll={ll}\tcorr={corr}\tlog_box={log_box}')
        return (ll - corr + log_box), phi


    return Proposal(__quantile, __correction)


def _process_stdev(stdev, mean, bounds):
    if isinstance(stdev, float):
        stdev = zeros(len(mean)) + stdev
    elif len(mean) != len(stdev):
        raise ValueError(
            'Proposal Mean and covariance are of incompatible lengths: ' +
            f'len(mean)={len(mean)} vs. len(stdev)={len(stdev)}')
    else:
        if len(stdev[0]) != len(mean):
            raise ValueError('Dimensions of covariance and mean don\'t match' +
                             f'len(stdev)={len(stdev)} vs len(mean)={len(mean)}')

    try:
        a, b = bounds
    except ValueError:
        a, b = bounds.T
        warnings.warn('Bounds should be transposed.')

    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        pass
    else:
        if len(a) != len(b):
            raise ValueError('Lopsided bounds: ' +
                             f'len(a)={len(a)} vs. len(b)={len(b)}')

        if 0 != len(a) != len(mean):
            raise ValueError(
                'Proposal mean and boundaries are of imcompatible lengths: ' +
                f'len(a)={len(a)} vs len(mean)={len(mean)}')


    return stdev, a, b
