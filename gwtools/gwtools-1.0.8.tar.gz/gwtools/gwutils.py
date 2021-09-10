# --- gwutils.py

"""
        A collection of useful gravitational wave tools
"""

from __future__ import division # for py2

__copyright__ = "Copyright (C) 2015 Jonathan Blackman"
__status__    = "testing"
__author__    = "Jonathan Blackman"

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

#for consistency, define global units
try:
  from lal import PC_SI, MSUN_SI, G_SI, C_SI
  SOLAR_DISTANCE = MSUN_SI*G_SI/(C_SI**2.)
  SOLAR_TIME     = SOLAR_DISTANCE/C_SI
except:
  PC_SI   = None
  MSUN_SI = None
  SOLAR_DISTANCE = None
  SOLAR_TIME = None

import numpy as np
from .harmonics import sYlm

###############################################################################
# Tapering windows

def _planckWindowFunction(t, tol=0.005):
    """f(t) = 0 if t < tol
            = 1 if t > 1 - tol
            = 1/(1 + exp(z)) otherwise, where z = 1/t - 1/(1-t)"""
    safe = (t > tol)*(t < (1. - tol))
    # temporarily set unsafe times to 0.5 to avoid dividing by 0
    safeT = safe*t + (1. - safe)*.5
    safeZ = 1./safeT - 1./(1. - safeT)
    return safe*1./(1. + np.exp(safeZ)) + (t >= (1.-tol))

#------------------------------------------------------------------------------

def _cosineWindowFunction(t):
    """f(t) = 0 if t < 0
            = 1 if t > 1
            = (1 - cos(pi*t))/2 otherwise"""
    return (t >= 1.) + (0. < t)*(t < 1.)*(1. - np.cos(np.pi*t))/2.

#------------------------------------------------------------------------------

def window(t, tStart=0., tEnd=1., rolloff=0, windowType='planck'):
    """Return a smooth rollon function, evaluated at an array of times t:
    When t <= tStart, f(t) = 0
    When t >= tEnd, f(t) = 1
    Otherwise, 0 <= f(t) <= 1, where f is monotonically increasing.

    If rolloff=1, reverse the window so that f(tStart) = 1, f(tEnd) = 0.

    windowType may be:
        'planck'
        'cosine'"""
    if rolloff:
        return window(-t, tStart=-tEnd, tEnd=-tStart, windowType=windowType)

    if tEnd==1. and tStart==0.:
        if windowType=='planck':
            return _planckWindowFunction(t)
        elif windowType=='cosine':
            return _cosineWindowFunction(t)
        else:
            raise ValueError('Unsupported window type: {0}'.format(windowType))

    return window((t - tStart)/(tEnd - tStart), windowType=windowType)

#------------------------------------------------------------------------------

def windowWaveform(t, h, t1, t2, t3, t4, windowType="planck"):
    """Rolls on from t1 to t2, then rolls off from t3 to t4.

    t1-t4 are assumed to have the same units as t.

    windowType can be:
        "planck"
        "cosine" """
    window1 = window(t, tStart=t1, tEnd=t2, windowType=windowType)
    window2 = window(t, tStart=t3, tEnd=t4, rolloff=1, windowType=windowType)
    return h*window1*window2

#------------------------------------------------------------------------------

def windowWaveformV2(t,h,t1=-2750., t2=-2500., t3=50., t4=90., windowType="planck", nSolarMasses=None):
  """ Wrapper around windowWaveform. Use when waveform independent variable
      units in seconds, while window parameters t1 - t4 are specified
      in dimensionless units.

      INPUT
      =====
      i)  nSolarMasses = None

        t1-t4 assumed to have the same units as t.

      ii) nSolarMasses = Mtot

        t1-t4 in dimensionless units. t in seconds"""
    
  if(nSolarMasses is not None):
    t1 = t1*SOLAR_TIME*nSolarMasses
    t2 = t2*SOLAR_TIME*nSolarMasses
    t3 = t3*SOLAR_TIME*nSolarMasses
    t4 = t4*SOLAR_TIME*nSolarMasses

  h_window = windowWaveform(t, h, t1, t2, t3, t4, windowType)
  return h_window

###############################################################################
# Obtaining frequency domain waveforms

def freqDomainWaveform(h, dt, dfMax=None, padLocation='start'):
    """A function to fft waveforms, always padding up to a power of 2 and
    possibly more.

    INPUT
    =====
    h            --- complex or real values numpy array (should be tapered!)
    dt           --- = 1/sampling_rate
    dfMax: If the waveform is not long enough, it will be padded with zeros
           until it achieves df <= dfMax.
           If None, only pad up to a power of 2.
    padLocation  --- 'start', 'center', 'end', 'random', and
                     determines where the zeros are placed

    OUTPUT
    =====
    frequencies: An array of monotonically increasing frequencies
    hf: The frequency domain waveform"""

    # Find a power of 2 that achieves dfMax
    minLength = len(h)
    if dfMax is not None:
        minLength = max(len(h), 1./(dt*dfMax))
    pow2 = 0
    while 2**pow2 < minLength:
        pow2 += 1

    nZeros = 2**pow2 - len(h)
    if padLocation == 'start':
        h = np.append(np.zeros(nZeros), h)
    elif padLocation == 'center':
        h = np.append(np.append(np.zeros(nZeros//2), h),
                      np.zeros(nZeros - nZeros//2))
    elif padLocation == 'end':
        h = np.append(h, np.zeros(nZeros))
    elif padLocation == 'random':
        start_zeroes = int(np.random.random() * nZeros)
        end_zeroes = nZeros - start_zeroes
        h = np.append(np.append(np.zeros(start_zeroes), h), np.zeros(end_zeroes))
    else:
        raise ValueError('padLocation not recognized')

    freqs = np.fft.fftfreq(len(h), dt)
    hFreq = np.fft.fft(h)*dt

    # The negative frequencies are at the end.  Reorder to be monotonic.
    idx = int( (len(freqs)+1)/2 ) # TODO: why was previous calls from write_data.py giving 4096.5?? Had to cast to int
    freqs = np.append(freqs[idx:], freqs[:idx])
    hFreq = np.append(hFreq[idx:], hFreq[:idx])
    return freqs, hFreq

#------------------------------------------------------------------------------

def freqDomainModes(h, dt, dfMax=None, padLocation='start'):
    """Similar to freqDomainWaveform, but where h is a 2-d array of
    complex modes (mode index first).

    The returned hf is an array of the fft of each mode."""

    # Find a power of 2 that achieves dfMax
    minLength = len(h[0])
    if dfMax is not None:
        minLength = max(len(h[0]), 1./(dt*dfMax))
    pow2 = 0
    while 2**pow2 < minLength:
        pow2 += 1

    nZeros = 2**pow2 - len(h[0])
    if padLocation == 'start':
        h = np.array([np.append(np.zeros(nZeros), mode) for mode in h])
    elif padLocation == 'center':
        h = np.array([np.append(np.append(np.zeros(nZeros//2), mode),
                                np.zeros(nZeros - nZeros//2)) for mode in h])
    elif padLocation == 'end':
        h = np.array([np.append(mode, np.zeros(nZeros)) for mode in h])
    elif padLocation == 'random':
        start_zeroes = int(np.random.random() * nZeros)
        end_zeroes = nZeros - start_zeroes
        h = np.array([np.append(np.append(np.zeros(start_zeroes), mode), np.zeros(end_zeroes)) for mode in h])
    else:
        raise ValueError('padLocation not recognized')

    freqs = np.fft.fftfreq(len(h[0]), dt)
    hFreq = np.array([np.fft.fft(mode)*dt for mode in h])

    # The negative frequencies are at the end.  Reorder to be monotonic.
    idx = int((len(freqs)+1)/2)
    freqs = np.append(freqs[idx:], freqs[:idx])
    hFreq = np.array([np.append(mode[idx:], mode[:idx]) for mode in hFreq])
    return freqs, hFreq

#------------------------------------------------------------------------------

def freqDomainWaveformFromModes(frequencies, hModes, theta, phi, kappa):
    """Given the fourier transforms of the waveform modes, evaluates the
    waveform on the sphere at (theta, phi) with polarization
    cos(2*kappa)*h_plus + sin(2*kappa)*h_cross

    INPUT
    =====
    frequencies: The uniformly spaced array of frequencies at which hModes
                 is evaluated, symmetrically spaced around 0Hz such that
                 frequencies[0] = -1*frequencies[-1].
    hModes: A 2-d array of frequency domain waveform modes, mode index first.
            The modes should be ordered [(2, -2), ..., (2, 2), (3, -3), ...]
    theta, phi: The spherical polar coordinates at which the waveform
                should be evaluated
    kappa: The polarization angle of the waveform."""

    # Make sure we have a symmetric uniformly spaced frequency array
    df = frequencies[1] - frequencies[0]
    maxErr = max(abs(df - np.diff(frequencies)))
    if maxErr > df*1.e-6:
        raise ValueError('frequencies should be uniformly spaced')
    if not 0. in frequencies:
        raise ValueError('frequencies should contain 0')
    if abs(frequencies[0] + frequencies[-1]) > 1.e-6*df:
        raise ValueError('frequencies should be symmetrically spaced about 0!')

    # if F[h] gives the fourier transform of h,
    # F[ \sum Y_{\ell, m} h^{\ell, m} ] = \sum Y_{\ell, m} F[h^{\ell, m}]
    lm = []
    l=2
    m=-2
    for _ in hModes:
        lm.append([l,m])
        m += 1
        if m > l:
            l += 1
            m = -l
    h_sphere = np.sum(np.array([sYlm(-2, l, m, theta, phi)*mode
                                for ((l, m), mode) in zip(lm, hModes)]), 0)

    # h_sphere is F[h_plus + i*h_cross] = F[h]
    # If hf = F[exp(-2i*kappa)*h] = exp(-2i*kappa)F[h],
    # then (hf(f) + hf(-f)*)/2 = F[real(exp(-2i*kappa)*h)]
    # = F[cos(2*kappa*h_plus) + i*sin(2*kappa*h_cross)]
    h_rotated = h_sphere*np.exp(-2.j*kappa)
    h_polarized = 0.5*(h_rotated + h_rotated[::-1].conjugate())
    return h_polarized

#------------------------------------------------------------------------------

def hp_hc_from_freqDomain_modes(frequencies, hModes, theta, phi):
    """Given the fourier transforms of the waveform modes, evaluates the
    two waveform polarizations on the sphere at (theta, phi)

    INPUT
    =====
    frequencies: The uniformly spaced array of frequencies at which hModes
                 is evaluated, symmetrically spaced around 0Hz such that
                 frequencies[0] = -1*frequencies[-1].
    hModes: A 2-d array of frequency domain waveform modes, mode index first.
            The modes should be ordered [(2, -2), ..., (2, 2), (3, -3), ...]
    theta, phi: The spherical polar coordinates at which the waveform
                should be evaluated"""

    # Make sure we have a symmetric uniformly spaced frequency array
    df = frequencies[1] - frequencies[0]
    maxErr = max(abs(df - np.diff(frequencies)))
    if maxErr > df*1.e-6:
        raise ValueError('frequencies should be uniformly spaced')
    i0 = np.argmin(abs(frequencies))
    if max(abs(frequencies[i0:] + frequencies[i0::-1])) > df*1.e-6:
        raise ValueError('frequencies should be symmetrically spaced about 0')

    # if F[h] gives the fourier transform of h,
    # F[ \sum Y_{\ell, m} h^{\ell, m} ] = \sum Y_{\ell, m} F[h^{\ell, m}]
    lm = []
    l=2
    m=-2
    for _ in hModes:
        lm.append([l,m])
        m += 1
        if m > l:
            l += 1
            m = -l
    h_sphere = np.sum(np.array([sYlm(-2, l, m, theta, phi)*mode
                                for ((l, m), mode) in zip(lm, hModes)]), 0)

    # h_sphere is F[h_plus] + i*F[h_cross]
    # h_sphere(-f)* is F[h_plus](-f) - i*F[h_cross](-f)
    # since h_plus and h_cross are real in the time domain
    h_plus = 0.5*(h_sphere[i0:] + h_sphere[i0::-1].conjugate())
    h_cross = 0.5j*(h_sphere[i0:] - h_sphere[i0::-1].conjugate())
    return h_plus, h_cross

###############################################################################
