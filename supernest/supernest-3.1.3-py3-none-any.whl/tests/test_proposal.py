import supernest
from pypolychord.settings import PolyChordSettings
from pypolychord import run_polychord
import scipy.stats as st
import matplotlib.pyplot as plt
import numpy as np
import mpi4py


def uniform_with_gaussian_like(nDims, mu, sigma, bounds):
    thetamin = bounds[0]
    thetamax = bounds[1]
    invCov = np.linalg.inv(sigma)

    def ll(theta):
        return -(theta - mu) @ invCov @ (theta - mu) / 2, []

    def up(cube):
        return thetamin + cube * (thetamax - thetamin)

    return up, ll


def normal_run_settings(nDims,
                        nlive,
                        file_root='control_uniform_gaussian_like'):
    settings = PolyChordSettings(nDims, 0)
    settings.read_resume = False
    settings.feedback = 0
    settings.nlive = nlive
    settings.file_root = file_root

    return settings


def test_uniform(nDims, mu, sigma, bounds, nlive):
    prior, like = uniform_with_gaussian_like(nDims, mu, sigma, bounds)

    settings = normal_run_settings(nDims, nlive)
    output = run_polychord(like, nDims, 0, settings, prior)
    return output, prior, like


def test_proposal(nDims, mu, sigma, bounds, nlive):
    prior, like = uniform_with_gaussian_like(nDims, mu, sigma, bounds)

    pp, ll = supernest.truncated_gaussian_proposal(bounds,
                                                   mu,
                                                   sigma,
                                                   loglike=like)
    settings = normal_run_settings(nDims,
                                   nlive,
                                   file_root="supernest_proposal")
    output = run_polychord(ll, nDims, 0, settings, pp)
    return output, pp, ll


def test_supernest(nDims, mu, sigma, bounds, nlive):
    prior, like = uniform_with_gaussian_like(nDims, mu, sigma, bounds)
    pp, ll = supernest.truncated_gaussian_proposal(bounds,
                                                   mu,
                                                   sigma,
                                                   loglike=like)
    dims, ppp, lll = supernest.superimpose([(prior, like), (pp, ll)], nDims)

    settings = normal_run_settings(dims,
                                   nlive,
                                   file_root="supernest_superimposed")

    output = run_polychord(lll, dims, 0, settings, ppp)
    return output, ppp, lll


def deltas(boundaries, nDims, mu, sigma, nlive):
    retZ = []
    retZerr = []
    for b in boundaries:
        bounds = (-b, b)
        uni = test_uniform(nDims, mu, sigma, bounds, nlive)[0]
        # pro = test_supernest(nDims, mu, sigma, bounds, nlive)[0]
        pro = test_proposal(nDims, mu, sigma, bounds, nlive)[0]
        retZ.append(uni.logZ - pro.logZ)
        retZerr.append(max(uni.logZerr, pro.logZerr))
    return retZ, retZerr


def test_truncated_gaussian(boundaries, nDims, mu, sigma):
    pp, _ = supernest.truncated_gaussian_proposal(boundaries,
                                                  mu,
                                                  sigma,
                                                  bounded=False)
    xs = np.linspace(0, 1, 100000)
    ys = np.array([pp(x) for x in xs])
    print(ys)
    yys = np.array([
        st.truncnorm.ppf(x, boundaries[0], boundaries[1], scale=sigma)
        for x in xs
    ])
    plt.figure()
    plt.hist(yys, alpha=0.8, label='scipy', bins=100)
    plt.hist(ys, alpha=0.8, label='supernest', bins=100)
    plt.legend()
    plt.show()


def main(a=1, it=5):
    global uniform, proposal, delta, x, deltaerr
    nlive = 120
    nDims = 2
    mu = np.array([0, 1])
    sigma = np.array([[1, 0], [0, 1]])
    bounds = (np.array([-a]), np.array([a]))
    x = np.linspace(0.001 * a, a, it)
    delta, deltaerr = deltas(x, nDims, mu, sigma, nlive)
    # test_truncated_gaussian(bounds, nDims, mu, sigma)


if __name__ == "__main__":
    main()
