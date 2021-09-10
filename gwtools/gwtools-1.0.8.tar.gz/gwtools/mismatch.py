# --- fitfuncs.py

"""
A collection of useful functions for comparing frequency  and time domain
waveforms and evaluating errors.
Throughout, "overlap_err" is 1 - overlap, NOT optimizing over time shifts,
and "mismatch" is (1 - overlap) minimized over time shifts.
Other parameters are not optimized unless explicitly stated in the docstring.

See docs/mismatches.pdf for mathematics.
"""

from __future__ import division # for python 2


__copyright__ = "Copyright (C) 2015 Jonathan Blackman"
__status__    = "testing"
__author__    = "Jonathan Blackman, Scott Field"

__license__ = """
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import numpy as np
from . import const
from .harmonics import sYlm
from scipy.interpolate import UnivariateSpline as uspline

###############################################################################
# Inner products

def inner_complex(h1, h2, psd=None, df=1.0, pos_freq=False, ligo=False):
    """Frequency domain weighted complex inner product.

    h1, h2 are frequency domain waveforms (complex 1d arrays).
    psd can be None for unweighted (equivalent to a psd of ones) or an array
    of values the same length as h1 and h2.
    Note: PSD = ASD^2, should be ~ 10^-42 (not 10^-21) for aLIGO.


    If pos_freq=True, h1 and h2 are interpreted as coming from f>=0 
    frequencies and are real function in the time-domain. Then 

      inner = 2 * Real(inner_complex)

    which comes from folding f<0 frequencies (accounts for "2 * Real()")


    If ligo=True we use the typical gw convention

        inner = 2 * inner_complex


    If ligo=True, pos_freq=True we use both of the above rules:

        inner_ligo = 4 * Real(inner_complex)


    See, for example,
            https://arxiv.org/pdf/1602.03839.pdf (Eq 1)
            https://arxiv.org/pdf/1602.03509.pdf (Eq 6)
            https://arxiv.org/pdf/gr-qc/0509116.pdf (Eq 4.1) """

    if psd is None:
        result = df * h1.dot(h2.conjugate())
    else:
        result = df * h1.dot(h2.conjugate()/psd)

    factor = 1.0
    if ligo:
        factor = factor*2.0

    if pos_freq:
        return 2.0 * factor * np.real(result)
    else:
        return factor * result

#-----------------------------------------------------------------------------

def inner(h1, h2, psd=None, df=1.0, pos_freq=False, ligo=False):
    """Real frequency domain inner product.
    See inner_complex for details."""

    return np.real(inner_complex(h1, h2, psd, df, ligo))

#-----------------------------------------------------------------------------

def inner_complex_timeshift_series(h1, h2, psd=None, n_zeros=0):
    """Uses an inverse fft to compute inner_complex of h1 and
    h2*exp(2*pi*i*f*dt) for dt=0, 1/f_max, 2/f_max, ..."""

    if n_zeros > 0:
        h1_z = np.append(h1, np.zeros(n_zeros))
        h2_z = np.append(h2, np.zeros(n_zeros))
        if psd is None:
            psd2 = None
        else:
            psd2 = np.append(psd, np.ones(n_zeros))

        return inner_complex_timeshift_series(h1_z, h2_z, psd=psd2)

    if psd is None:
        return np.fft.fft(h1*h2.conjugate())
    return np.fft.fft(h1*h2.conjugate()/psd)

#-----------------------------------------------------------------------------

def inner_timeshift_series(h1, h2, psd=None, n_zeros=0):
    """Real part of inner_complex_timeshift_series"""

    return np.real(inner_complex_timeshift_series(h1, h2, psd, n_zeros))

#-----------------------------------------------------------------------------


###############################################################################
# h conversions

def modes_to_hf(h_modes, theta, phi):
    """Sums spin-weighted spherical harmonic modes (s=-2) evaluated at
    (theta, phi) to obtain the waveform.

    h_modes: A 2d array with shape (n_modes, n_samples), ordered
        [(2, -2), ..., (2, 2), (3, -3), ..., (3, 3), ...]

    returns hf, a 1d array with length n_samples."""

    L, m = 2, -2
    coefs = 1.j*np.zeros(len(h_modes))
    for i in range(len(h_modes)):
        coefs[i] = sYlm(-2, L, m, theta, phi)
        m += 1
        if m > L:
            L += 1
            m = -L

    if m != -L:
        raise Exception("Incomplete set of modes! Missing (%s, %s)"%(L, m))

    return coefs.dot(h_modes)

#-----------------------------------------------------------------------------

###############################################################################
# Utility

def _cyclic_quadratic_peak(y):
    """Finds the peak value of y using a quadratic curve through the max
    value and its neighbors. Assumes periodic boundary conditions if the max
    is at the edge.
    Returns i_peak (float), y_peak."""

    n = len(y)
    idx = np.argmax(y)
    y0 = y[idx]
    rp1 = y[(idx+1)%n] - y0
    rm1 = y[(idx-1)%n] - y0
    b = 0.5*(rp1 - rm1)
    c = 0.5*(rp1 + rm1)
    if c==0.:
        print('Warning: no quadratic term present in time optimization, using argmax')
        return idx, y0
    y_peak = y0 - 0.25*b*b/c
    i_peak = idx - 0.5*b/c
    return i_peak, y_peak

#-----------------------------------------------------------------------------

def _timeshift(df, nsamples, i_peak):
    """Finds the timeshift from inverse fft information"""
    dt = i_peak/(df*nsamples)
    if i_peak > 0.5*nsamples:
        dt -= 1./df
    return dt

#-----------------------------------------------------------------------------

def _cyclic_interp_phase(x, i_interp):
    """
    Uses a cubic spline to interpolate the angle of x onto the
    "index" i_interp which can be a float.
    Uses periodic boundary conditions.
    """

    i0 = int(i_interp)
    x2 = np.unwrap(np.angle(np.roll(x, -i0+1)[:4]))
    return uspline(np.array([-1., 0., 1., 2.]), x2, s=0)(np.array([i_interp - i0]))[0]

###############################################################################

def overlap_err(h1, h2, psd=None):
    n1 = inner(h1, h1, psd)
    n2 = inner(h2, h2, psd)
    return 1. - inner(h1, h2, psd)/np.sqrt(n1*n2)

#-----------------------------------------------------------------------------

def mismatch(h1, h2, psd=None, df=1., polarization_shift=True):
    """
    Minimizes the overlap error over time shifts and (possibly)
    polarization angle shifts.
    Returns:
        mismatch
        time shift
        polarization angle shift (returns zero if polarization_shift is False)
    If df is in Hz, the returned time shift is in seconds.
    A quadratic fit to the largest overlap and its nearest neighbors is used
    to determine the maximum, but be sure the waveforms are long enough
    (pad with zeros if needed) to get a good time-shift resolution!
    """

    n1 = inner(h1, h1, psd)
    n2 = inner(h2, h2, psd)
    d = inner_complex_timeshift_series(h1, h2, psd)
    if polarization_shift:
        i_max, d_max = _cyclic_quadratic_peak(abs(d))
        psi = 0.5 * _cyclic_interp_phase(d, i_max)
    else:
        i_max, d_max = _cyclic_quadratic_peak(np.real(d))
        psi = 0.
        
    dt = _timeshift(df, len(d), i_max)
    return 1. - d_max/np.sqrt(n1*n2), dt, psi
        

#-----------------------------------------------------------------------------


# These functions will compute CalE and related quantities for a dictionary of modes

def total_amplitude_from_mode_dict(mode_dict):
    """Integrates |h^2(t)| over the sphere and takes the square root.
    
    Input: dictionary of modes as a time series, {mode1:timeseries_of_mode1,...}
    Output: time series of total waveform amplitude
    """
    amp_sqr = np.zeros(len(list(mode_dict.values())[0]))
    #print(len(mode_dict.values()[0]))
    #amp_sqr = np.zeros(len(mode_dict))
    #print(amp_sqr.shape)
    for v in mode_dict.values():
        #print(v.shape)
        amp_sqr += abs(v)**2
    return np.sqrt(amp_sqr)

def error_vs_time_from_mode_dict(ref_modes, other_modes):
    """Computes the square root of (|\delta h(t)|^2 integrated over the sphere).
    
    Input: dictionary of modes (e.g. {mode1:timeseries_of_mode1,...})
           from a reference (true) waveform, ref_mode, and a second waveform
           model, other_modes
           
    Output: time series of waveform error (see mathcal_E_error_from_mode_dict)
    
    """
    err = np.zeros(len(list(ref_modes.values())[0]))
    #print(len(ref_modes.values()[0]))
    #err = np.zeros(len(ref_modes))
    for k, v in ref_modes.items():
        if k in other_modes:
            d = v - other_modes[k]
            err += np.abs(d*d.conjugate())
            #err += abs(v - other_modes[k])**2
        else:
            err += abs(v)**2
    #print(np.sum(err))
    return np.sqrt(err)

def mathcal_E_error_from_mode_dict(ref_modes, other_modes):
    """ Computes Eq 21 from https://arxiv.org/pdf/1701.00550.pdf 
    
    This error is the "natural" time-domain error for multi-mode signals
    
    Input: dictionary of modes (e.g. {mode1:timeseries_of_mode1,...})
           from a reference (true) waveform, ref_mode, and a second waveform
           model, other_modes
           
    Output: the error, a single number
    """
    amp = total_amplitude_from_mode_dict(ref_modes)
    #print(np.sum(amp**2))
    err = error_vs_time_from_mode_dict(ref_modes, other_modes)
    #print(np.sum(err**2))
    return 0.5 * np.sum(err**2) / np.sum(amp**2)

def mathcal_E_mode_contributions_from_mode_dict(ref_modes, other_modes):
    """ Mode-by-mode contributions to mathcal E error.
    
    The sum of all these error contributions should equal the 
    value from mathcal_E_error_from_mode_dict
    
    Input: dictionary of modes (e.g. {mode1:timeseries_of_mode1,...})
           from a reference (true) waveform, ref_mode, and a second waveform
           model, other_modes
           
    Output: the error in each mode, such that the sum is equal to mathcalE error
    """
    
    def mode_diff(ref_modes, other_modes):
        diff = {}
        for k, v in ref_modes.items():
            if k in other_modes:
                v2 = other_modes[k]
            else:
                v2 = 0.
            diff[k] = v - v2
        return diff
    
    amp = total_amplitude_from_mode_dict(ref_modes)
    denom = np.sum(amp**2)
    mode_diffs = mode_diff(ref_modes, other_modes)
    contributions = {}
    for k, v in mode_diffs.items():
        contributions[k] = 0.5 * np.sum(abs(v)**2) / denom
    return contributions

def mathcal_E_error_from_mode_list(h1, h2):
    """  time-domain error via Eq 21 https://arxiv.org/pdf/1701.00550.pdf 
    
    
    This error is the "natural" time-domain error for multi-mode signals
    
    Input: list of modes from a reference (true) waveform, h2, and a second waveform
           model, h1. It is assumed that lists h1 and h2 have the same mode ordering.
           
           mode0: h1[0],h2[0]
           mode1: h1[1],h2[1]
           ....

           The function will also accept single modes as a numpy array
           
    Output: the error, a single number
    """
    
    if isinstance(h1,list):
        assert(len(h1)==len(h2)) # lists should contain the same number of modes
    else:
        assert(isinstance(h1,np.ndarray))
    
    n1Sqr = np.sum(abs(h1**2))
    n2Sqr = np.sum(abs(h2**2))

    dots = np.array([(h1[i]*(h2[i].conjugate())) for i in range(len(h1))])
    sdot = np.real(np.sum(dots))  # THIS LINE CHANGED
    #sdot = np.real(h1.dot(h2.conjugate()))
    #sdot = np.sum(dots)
    #print(sdot)
    # Assume h1 is the reference waveform and normalize by its magnitude
    normed_errs = ((n1Sqr + n2Sqr) - 2*sdot)/(2*n1Sqr)
    summed_err = np.sum(normed_errs)
    return summed_err