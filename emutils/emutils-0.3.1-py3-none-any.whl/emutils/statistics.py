import warnings

from typing import Iterable

import numpy as np
import pandas as pd
import scipy.stats as st
from tqdm import tqdm

# Distributions to check
DISTRIBUTIONS = [
    st.alpha, st.anglit, st.arcsine, st.beta, st.betaprime, st.bradford, st.burr, st.cauchy, st.chi, st.chi2, st.cosine,
    st.dgamma, st.dweibull, st.erlang, st.expon, st.exponnorm, st.exponweib, st.exponpow, st.f, st.fatiguelife, st.fisk,
    st.foldcauchy, st.foldnorm, st.genlogistic, st.genpareto, st.gennorm, st.genexpon, st.genextreme, st.gausshyper,
    st.gamma, st.gengamma, st.genhalflogistic, st.gilbrat, st.gompertz, st.gumbel_r, st.gumbel_l, st.halfcauchy,
    st.halflogistic, st.halfnorm, st.halfgennorm, st.hypsecant, st.invgamma, st.invgauss, st.invweibull, st.johnsonsb,
    st.johnsonsu, st.ksone, st.kstwobign, st.laplace, st.levy, st.levy_l, st.levy_stable, st.logistic, st.loggamma,
    st.loglaplace, st.lognorm, st.lomax, st.maxwell, st.mielke, st.nakagami, st.ncx2, st.ncf, st.nct, st.norm,
    st.pareto, st.pearson3, st.powerlaw, st.powerlognorm, st.powernorm, st.rdist, st.reciprocal, st.rayleigh, st.rice,
    st.recipinvgauss, st.semicircular, st.t, st.triang, st.truncexpon, st.truncnorm, st.tukeylambda, st.uniform,
    st.vonmises, st.vonmises_line, st.wald, st.weibull_min, st.weibull_max, st.wrapcauchy
]


# Create models from data
def best_fit_distribution(
    data: pd.Series, ax=None, verbose=False, bins=20, skip_distributions=['gausshyper', 'levy_stable']
):
    """Model data by finding best fit distribution to data"""
    # Get histogram of original data
    y, x = np.histogram(data, bins=bins, density=True)
    x = (x + np.roll(x, -1))[:-1] / 2.0

    # Best holders
    best_distribution = st.norm
    best_params = (0.0, 1.0)
    best_sse = np.inf

    # Estimate distribution parameters from data
    iters = enumerate(DISTRIBUTIONS)
    if verbose:
        iters = tqdm(iters, total=len(DISTRIBUTIONS))
    for d, distribution in iters:
        if distribution.name in skip_distributions:
            continue
        iters.set_description(f'Fitting distributions ({distribution.name})')
        # Try to fit the distribution (if possible, otherwise skip it)
        try:
            # Ignore warnings from data that can't be fit
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')

                # fit dist to data
                params = distribution.fit(data)

                # Separate parts of parameters
                arg = params[:-2]
                loc = params[-2]
                scale = params[-1]

                # Calculate fitted PDF and error with fit in distribution
                pdf = distribution.pdf(x, loc=loc, scale=scale, *arg)
                sse = np.sum(np.power(y - pdf, 2.0))

                # If we have a matplotlib ax, then we plot the distribution
                try:
                    if ax is not None:
                        pd.Series(pdf, x).plot(ax=ax, label=distribution.name)
                except Exception:
                    pass

                # identify if this distribution is better
                if best_sse > sse > 0:
                    best_distribution = distribution
                    best_params = params
                    best_sse = sse

        except Exception:
            if verbose:
                print(f'Could not fit {distribution.name}')

    iters.set_description(
        f'Fitted \'{best_distribution.name}\' distribution {tuple([round(p, 3) for p in best_params])}'
    )
    iters.refresh()

    return (best_distribution, best_params)


def make_pdf(dist, params, size=10000):
    """Generate distributions's Probability Distribution Function """

    # Separate parts of parameters
    arg = params[:-2]
    loc = params[-2]
    scale = params[-1]

    # Get sane start and end points of distribution
    start = dist.ppf(0.01, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.01, loc=loc, scale=scale)
    end = dist.ppf(0.99, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.99, loc=loc, scale=scale)

    # Build PDF and turn into pandas Series
    x = np.linspace(start, end, size)
    y = dist.pdf(x, loc=loc, scale=scale, *arg)
    pdf = pd.Series(y, x)

    return pdf