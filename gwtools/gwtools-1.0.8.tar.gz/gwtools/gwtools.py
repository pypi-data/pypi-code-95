# --- gwtools.py ---

"""
	A collection of useful gravitational wave tools
"""

from __future__ import division # for python 2


__copyright__ = "Copyright (C) 2014 Scott Field and Chad Galley"
__email__     = "sfield@astro.cornell.edu, crgalley@tapir.caltech.edu"
__status__    = "testing"
__author__    = "Scott Field, Chad Galley"

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
from scipy.interpolate import interp1d
from scipy.optimize import minimize
import scipy.integrate as sp 
from scipy.interpolate import InterpolatedUnivariateSpline as spline
import warnings as _warnings


# Define global constants
from . import const
PC_SI     = const.PCinm   # Parsec in meters
c         = const.c
G         = const.G
MSUN_SI   = const.Msun
Msuninsec = const.Msuninsec


#####################################
# Functions for changing parameters #
#####################################

def m1m2_to_Mc(m1,m2):
    """Chirp mass from m1, m2"""
    return (m1*m2)**(3./5.)/(m1+m2)**(1./5.)


def m1m2_to_nu(m1,m2):
    """Symmetric mass ratio from m1, m2"""
    return m1*m2/(m1+m2)**2


def m1m2_to_Mcnu(m1, m2):
  """Compute symmetric mass ratio and chirp mass from m1, m2"""	
  return m1m2_to_Mc(m1,m2), m1m2_to_nu(m1,m2)


def q_to_nu(q):
  """Convert mass ratio (which is >= 1) to symmetric mass ratio"""
  return q / (1.+q)**2.


def nu_to_q(nu):
  """Convert symmetric mass ratio to mass ratio (which is >= 1)"""
  return (1.+np.sqrt(1.-4.*nu)-2.*nu)/(2.*nu)


def Mq_to_m1m2(M, q):
  """Convert total mass, mass ratio pair to m1, m2"""
  m2 = M/(1.+q)
  m1 = M-m2
  return m1, m2


def Mq_to_Mc(M, q):
  """Convert mass ratio, total mass pair to chirp mass"""
  return M*q_to_nu(q)**(3./5.)


def Mcq_to_M(Mc, q):
  """Convert mass ratio, chirp mass to total mass"""
  return Mc*q_to_nu(q)**(-3./5.)


def Mcnu_to_M(Mc, nu):
  """Convert chirp mass and symmetric mass ratio to total mass"""
  return Mc*nu**(-3./5.)

def Mnu_to_Mc(M, nu):
  """Convert total mass and symmetric mass ratio to chirp mass"""
  return M*nu**(3./5.)

def Mnu_to_m1m2(M, nu):
  """Convert total mass and symmetric mass ratio to m1, m2"""
  q      = nu_to_q(nu)
  m1, m2 = Mq_to_m1m2(M,q) # m1 > m2. m1 and m2 will be SI
  return m1, m2

def Mcnu_to_m1m2(Mc, nu):
  """Convert chirp mass, symmetric mass ratio pair to m1, m2"""
  q = nu_to_q(nu)
  M = Mcq_to_M(Mc, q)
  return Mq_to_m1m2(M, q)

def m1m2_to_delta(m1, m2):
  """Convert m1, m2 pair to relative mass difference [delta = (m1-m2)/(m1+m2)]"""
  return (m1-m2)/(m1+m2)


def q_to_delta(q):
  """Convert mass ratio (which is >= 1) to relative mass difference (delta)"""
  return (q-1.)/(q+1.)


def delta_to_q(delta):
  """Convert relative mass difference (delta) to mass ratio q (q >= 1)"""
  return (1.+delta)/(1.-delta)


def delta_to_nu(delta):
  """Convert relative mass difference (delta) to symmetric mass ratio"""
  return (1.-delta**2)/4.


def nu_to_delta(nu):
  """Convert symmetric mass ratio to relative mass difference delta"""
  return np.sqrt(1.-4.*nu)


def X1X2_to_Xs(X1, X2):
  """Convert dimensionless spins X1, X2 to symmetric spin Xs"""
  return (X1+X2)/2.


def X1X2_to_Xa(X1, X2):
  """Convert dimensionless spins X1, X2 to anti-symmetric spin Xa"""
  return (X1-X2)/2.


def X1X2_to_XsXa(X1, X2):
  """Convert dimensionless spins X1, X2 to symmetric and anti-symmetric spins Xs, Xa"""
  return X1X2_to_Xs(X1,X2), X1X2_to_Xa(X1,X2)

def Chi1M1Chi2M2_to_chiE(chi1,m1,chi2,m2):
  """Convert (chi_i,m_i) pair to chi_effective"""
  M = m1+m2
  return ( m1 * chi1 + m2 * chi2) / M

##################################
# Miscellaneous helper functions #
##################################

def fgwisco(Mtot):
  """GW frequency at ISCO. [Note: Maggiore's text has an extra 1/2.]"""
  return 6.0**(-1.5) / (np.pi*Mtot)


def get_arg(a, a0):
  """Get argument at which a0 occurs in array a"""
  return np.argmin(np.abs(a-a0))


def get_peak(x, y):
  """Get argument and values of x and y at maximum value of |y|"""
  arg = np.argmax(y)
  return [arg, x[arg], y[arg]]


def all_zero_crossings(x):
  pos = x > 0
  npos = ~pos
  return ((pos[:-1] & npos[1:]) | (npos[:-1] & pos[1:])).nonzero()[0]


def fit_peak(x, y, fit='polyfit', a=10, b=10, deg=2, num=1000):
  """
  Estimate peak of y through interpolation.
  
  Input
  =====
  x   --- x data array (1d)
  y   --- y data array (1d)
  fit --- Type of fitting function 
          (default='polyfit')
  a   --- Number of points to fit before estimated peak
          (default=10)
  b   --- Number of points to fit after estimated peak 
          (default=10)
  deg --- Degree or order of fitting function 
          (default=2)
  num --- Number of high resolution x samples for estimating peak 
          (default=1000)
  
  Output
  ======
  x_peak --- Estimated x value of the estimated maximum of y data
  y_peak --- Estimated maximum of y data
  
  Note: The fitting is currently done with the UnivariateFits class 
  in ROMpy. The maximum of the y data is estimated by evaluating the 
  fitting function at num(=1000) points. However, the default fitting 
  function is a quadratic polynomial, the peak of which is 
  calculated analytically instead of numerically.
  """
  
  try:
    from rompy.univar import UnivariateFits
  except:
    raise Exception("Cannot import UnivariateFits class from RomPy.")
  
  # Get argument of discrete data y
  try:
    from rompy.derivatives import D
  except:
    raise Exception("Cannot import D function for computing finite differences from RomPy.")

  arg = np.argmax(y)
  if arg-a < 0:
    a = arg
  if arg+b > len(y):
    b = 0
  x_fit = x[arg-a:arg+b+1]
  y_fit = y[arg-a:arg+b+1]
  
  # Determine if the data in this range has a maximum
  dy = D(y_fit, x_fit, dx=1, order=4)
  d2y = D(y_fit, x_fit, dx=2, order=4)
  i0 = all_zero_crossings(dy)
  if len(i0) == 0:
    raise Exception("Did not find an extremum in the input data except possibly at endpoints.")
  elif len(i0) > 1:
    raise Exception("Found more than one extremum in the input data.")
  elif len(i0) == 1:
    # Positive concavity implies a minimum
    if d2y[i0] > 0.:
      raise Exception("Did not find a maximum in the input data.")
    # Zero concavity implies an inflection point
    elif d2y[i0] == 0.:
      raise Exception("Extremum is an inflection point.")
    # Negative concavity implies a maximum, so continue on
  else:
    raise Exception("Cannot determine the nature of the data. Please check the input.")
  
  # Fit over the interval around arg using the requested fitting function
  _fit = UnivariateFits(x_fit, y_fit, fit=fit, deg=deg)
  if fit == 'polyfit' and deg == 2:
    c, b, a = _fit._eval
    x_peak = -b/(2.*c)
  else:
    x_fine = np.linspace(x_fit[0], x_fit[-1], num)
    x_peak = x_fine[np.argmax(_fit.eval(x_fine))]
  
  y_peak = _fit.eval(x_peak)
  return x_peak, y_peak


def chop(x, y, xmin, xmax):
  """Chop arrays x, y for x in [xmin, xmax]"""
  argmin = get_arg(x, xmin)
  argmax = get_arg(x, xmax)
  return x[argmin:argmax+1], y[argmin:argmax+1]


def shift(x, xshift):
  """Shift array x by xshift"""
  arg = get_arg(x, xshift)
  return x-x[arg]


def shift_chop(x, y, xshift, xmin, xmax):
  """Shift x, y arrays by xshift then chop for x in [xmin, xmax]"""
  xnew = shift(x, xshift)
  xminnew = xmin-xshift
  xmaxnew = xmax-xshift
  #return chop(xnew, y, xminnew, xmaxnew)
  return chop(xnew, y, xmin, xmax)


def amp(h):
  """Get amplitude of waveform, h = A*exp(i*phi)"""
  return np.abs(h)


def amp_phase(h):
  """Get amplitude and phase of waveform, h = A*exp(i*phi)"""
  amp = np.abs(h);
  return amp, phase(h)


def phase(h):
  """Get phase of waveform, h = A*exp(i*phi)"""
  if np.shape(h):
    # Compute the phase only for non-zero values of h, otherwise set phase to zero.
    nonzero_h = h[np.abs(h) > 1e-300]
    phase = np.zeros(len(h), dtype='double')
    phase[:len(nonzero_h)] = np.unwrap(np.real(-1j*np.log(nonzero_h/np.abs(nonzero_h))))
  else:
    nonzero_h = h
    phase = np.real(-1j*np.log(nonzero_h/np.abs(nonzero_h)))
  return phase


def cycles(h):
  """Count number of cycles (to merger, if present) in waveform"""
  phi = phase(h)
  ipk, phi_pk, A_pk = get_peak(phi, np.abs(h))
  return (phi_pk - phi[0])/(2.*np.pi)


def hplus(h):
  """Get real part of waveform, h = A*exp(i*phi)"""
  return np.real(h)


def hcross(h):
  """Get imaginary part of waveform, h = A*exp(i*phi)"""
  return np.imag(h)


def logd(t,f):
  """Compute a logarithmic derivative"""
  dfdt = np.diff(f)/np.diff(t)
  return t[1:], dfdt/f[1:]


def plot_pretty(time, y, fignum=1, flavor='linear', color='k', linestyle=['-', '--'], \
        label=['$h_+(t)$', '$h_\\times(t)$'], legendQ=True, showQ=False):
  """create a waveform figure with nice formatting and labels.
  returns figure method for saving, plotting, etc."""

  try:
    import matplotlib.pyplot as plt
  except:
    raise Exception("Cannot import matplotlib.")
  
  # Plot waveform
  fig = plt.figure(fignum)
  ax = fig.add_subplot(111)
  
  dim_y = np.shape(y)
  num_y = len(dim_y)
  num_color, num_label = np.size(color), np.size(label)
  dim_linestyle = np.shape(linestyle)
  
  if num_y > 2:
    raise ValueError("Can only plot one or two functions")
  
  for ii in range(num_y):
    
    if num_y == 1: yy = y
    else: yy = y[ii]
    
    if num_color == 1: cc = color
    else: cc = color[ii]
    
    if num_label == 1: ll = label
    else: ll = label[ii]
    
    if len(dim_linestyle) == 0: ss = linestyle
    elif len(linestyle) == 1: ss = linestyle[0]
    else: ss = linestyle[ii]
    
    if flavor == 'linear':
      if legendQ:
        plt.plot(time, yy, color=cc, linestyle=ss, label=ll)
      else:
        plt.plot(time, yy, color=cc, linestyle=ss)
      
    elif flavor == 'semilogy':
      if legendQ:
        plt.semilogy(time, yy, color=cc, linestyle=ss, label=ll)
      else:
        plt.semilogy(time, yy, color=cc, linestyle=ss)
        
    elif flavor == 'semilogx':
      if legendQ:
        plt.semilogx(time, yy, color=cc, linestyle=ss, label=ll)
      else:
        plt.semilogx(time, yy, color=cc, linestyle=ss)
    
    elif flavor == 'loglog':
      if legendQ:
        plt.loglog(time, yy, color=cc, linestyle=ss, label=ll)
      else:
        plt.loglog(time, yy, color=cc, linestyle=ss)
    
    else:
      raise ValueError("Not a valid plot type")
  
  plt.xlabel('Time')
  plt.ylabel('Waveform')
  
  if legendQ:
    plt.legend(loc='upper left')
  
  if showQ:
    plt.show()
  
  return fig


def ecc_estimator(t,h,fit_window,type=1,fit_deg=1):
  """"Estimate the eccentricity associated with gravitational 
  waveform h from Eq. (17) of arxiv:1004.4697 (gr-qc)."""
    
  ### TODO: add butterworth filter for fit residuals. what would amplitude estimator look like?
    
  ### crop h to fit interval ###
  ecc_interval = np.arange(fit_window[0],fit_window[1])
  t            = t[ecc_interval]
  h            = h[ecc_interval]
  
  if type == 1:
    
    ### fit phase with degree fit_deg polynomial on fit_window ###
    amp_tmp, phase = get_amp_phase(h)
    p_coeff        = np.polyfit(t,phase,fit_deg)
    phase_fit      = np.polyval(p_coeff,t)
    
    ### compute the estimator ###
    ecc_est = ( phase - phase_fit ) / 4.
    
    return t, ecc_est
    
  elif type == 2:
    
    amp_tmp        = amp(h)
    t, amp_log     = logd(t,amp_tmp) # t will be one element shorter than before
    p_coeff        = np.polyfit(t,amp_log,fit_deg)
    amplog_fit     = np.polyval(p_coeff,t)
    
    return t, (amp_log - amplog_fit)


def find_instant_freq(hp, hc, t):
  """instantaneous starting frequency for 

              h = A(t) exp(2 * pi * i * f(t) * t), 

      where we approximate \partial_t A ~ \partial_t f ~ 0."""

  h    = hp + 1j*hc
  dt   = t[1] - t[0]
  hdot = (h[2] - h[0]) / (2 * dt) # 2nd order derivative approximation at t[1]

  f_instant = hdot / (2 * np.pi * 1j * h[1])
  f_instant = f_instant.real

  return f_instant


def dimensionless_time(M,t,UnitsOfM='s'):
  """ input time and mass in seconds. Returns dimensionless time """
  # TODO: input M could be in solar masses or 
  if UnitsOfM=='s':
    return t/M
  else:
    raise ValueError("Unknown units of M")

def dimensionless_frequency(M,f):
  """ Input frequency in seconds, Mass in solar masses. Returns dimensionless frequency"""
  return f * Msuninsec * M

def remove_amplitude_zero(t,h):
  """ removes h[i] t[i] from array if |h[i]| = 0 """
  
  amp, phase     = amp_phase(h)
  where_non_zero = np.nonzero(amp)
  
  return t[where_non_zero], h[where_non_zero]


def modify_phase(h,offset):
  """ Modify GW mode's phase to be \phi(t) -> \phi(t) + offset.
      For h_{ell,m}, typically offset = m*z_rot where z_rot is a 
      physical rotation about the z-axix (orthogonal to the orbital plane)."""
  return  h*np.exp(1.0j * offset)


def coordinate_time_shift(t,offset):
  """ Modify times to be t -> t + offset """
  return t + offset


def find_common_time_window(t1,t2):
  """ Given two temporal grids, find the largest range of common times 
      defined by [min_common,max_common] """

  min_common = max( t1[0], t2[0] )
  max_common = min( t1[-1], t2[-1] )
  
  if (max_common <= min_common):
    raise ValueError("there is no common time grid")
  
  return min_common, max_common


def simple_align_params(t1,h1,t2,h2):
  """ t1 times for complex waveform h1. 
  
      This routine returns simple alignment parameters 
      deltaT and deltaPhi by...
        (i)  fining discrete waveform peak
        (ii) aligning phase values at the peak time """
  
  amp1,phase1 = amp_phase(h1)
  amp2,phase2 = amp_phase(h2)
  
  deltaT   = t1[np.argmax( amp1 )] - t2[np.argmax( amp2 )]
  deltaPhi = phase1[np.argmax( amp1 )] - phase2[np.argmax( amp2 )]
  
  return deltaT, deltaPhi


def euclidean_norm_sqrd(f,dx):
  """ Euclidean norm squared of a complex vector f """
  return (np.sum(f*np.conj(f)) * dx).real

def euclidean_rel_error_sqrd(f1,f2,dx):
  """ Relative error 

            || f2 - f1||^2 / ( ||f1|| * ||f2|| )

computed from complex vectors f1 and f2 """

  err     = euclidean_norm_sqrd(f2-f1,dx)
  norm_f1 = np.sqrt(euclidean_norm_sqrd(f1,dx))
  norm_f2 = np.sqrt(euclidean_norm_sqrd(f2,dx))

  return err/(norm_f1*norm_f2)

def euclidean_norm_sqrd_2sphere(f,dx):
  """ Euclidean norm squared of a complex function 
  
      h(t,theta,phi) = \sum h_{ell,m}(t) B_{ell,m} (theta,phi) 

      known through its harmonic coefficients h_{ell,m}, each
      of which are column vector of an input matrix f."""

  full_norm = 0.0
  for ii in range(f.shape[1]):
    full_norm += euclidean_norm_sqrd(f[:,ii],dx)
    
  return full_norm


def generate_parameterize_waveform(t,h1_func,h1_type,h1_params=None):
  """ returns function for h(t;tc,phic) evaluations.

  INPUT
  =====
  t         --- array of times
  h1_func   --- waveform which can be evaluated for input set of times 
  h1_type   --- h1_func type ('interp1d','h_sphere') 
  h1_params --- any additional parameters needed for waveform evalautions"""

  if h1_type == 'interp1d': # interpolant built from scipy.interpolate.interp1d(t,h1_data)
    def parameterize_waveform(x):
      tc   = x[0]
      phic = x[1]
      try:
        t_shift = coordinate_time_shift(t,tc)
        h1_eval = h1_func( t_shift ) # differing sign from minimize_norm_error is correct
      except ValueError:
        msg_str="Cannot do h1_func( coordinate_time_shift(t,tc) ) \nmax(t_shift) = %e, min(t_shift) = %e, tc = %e"%(np.max(t_shift), np.min(t_shift), tc)
        raise(ValueError(msg_str))
      h1_eval = modify_phase(h1_eval,-phic)
      return h1_eval
      
  elif h1_type == 'h_sphere': # waveform from h_sphere_builder
    theta = h1_params
    def parameterize_waveform(x):
      tc   = x[0]
      phic = x[1]
      times = coordinate_time_shift(t,tc)
      hp,hc = h1_func(times,theta=theta, phi=0.0, z_rot=phic, psi_rot=None)
      return hp + 1.0j*hc

  else:
    raise ValueError('unknown waveform type')

  return parameterize_waveform


def generate_parameterized_norm(h1,h_ref,mynorm,t=None):
  """ 
  this routine will return a parameterized discrete norm 

         N(p1,p2,...) = || h1(p1,p2,...) - h_ref || 

  which can be minimized over the parameters (p1,p2...). If p1 = p2 = ... = 0 then 
  the norm is simply

                 || h1 - h_ref ||   for h1 = h1[t]

  h_ref is a reference waveform (represented by a discrete set
  evaluations) to which we match another waveform h1 (represented as a
  function). 

  h1 is a python function which takes inputs p1, p2,...
  where, typically, p1 is timeshift (tc) and p2 is a rotation about 
  the z-axis phic. The function h1 returns a vector h1(t_c,phi_c) collocated
  with h2_ref.


  Input
  =====
  t:         array of times such that h2_ref = h_ref[t]
  h2_ref:    array of reference waveform evaluations
  h1:        parameterized waveform function 
  mynorm:    function s.t. mynorm(f,dt) is a discrete norm


  Input expectations
  ==================
  (i) h1 should be defined on a larger temporal grid 
      than t and, hence, h2_ref. Why? When looking for the 
      minimum, h1 will be evaluated at times t + deltaT. 
      t should be viewed as the "common set of times" on which both 
      h1 and h_ref are known. """

  dt = 1.0 # we optimize the relative errors, factors of dt cancel

  # TODO: should check for TypeError by seeing if parameterized waveform can be evaluated by passing single x
  def ParameterizedNorm(x):
    h1_trial = h1(x)
    diff_h = h1_trial - h_ref
    
    # normalize by h2_ref as its fixed. Goal is to match h1 to h_ref #
    # TODO: perhaps divide by norm of h1_trial too, or pass in more general function to this routine
    overlap_errors = mynorm(diff_h,dt)/mynorm(h_ref,dt) 
    
    return overlap_errors

  return ParameterizedNorm


def create_common_time_grid(t1,t2,t_low_adj,t_up_adj):
  """ from temporal grids t1 and t2, create grid of common times"""

  common_dt      = (t1[2] - t1[1]) # TODO: t2 or t1 or variable
  t_start, t_end = find_common_time_window(t1,t2)
  common_times   = np.arange(t_start+t_low_adj,t_end-t_up_adj,common_dt) # small buffer needed 

  return common_times, t_start, t_end, common_dt


def discrete_minimization_from_discrete_waveforms(t,h,t_ref,h_ref):
  deltaT, deltaPhi = simple_align_params(t,h,t_ref,h_ref)
  h                = modify_phase(h,-deltaPhi)
  t                = coordinate_time_shift(t,-deltaT) # different sign from generate parameterize norm is correct

  return deltaT, deltaPhi, t, h


def setup_minimization_from_discrete_waveforms(t1,h1,t2,h2,t_low_adj,t_up_adj,verbose=False):

  t1, h1 = remove_amplitude_zero(t1,h1)
  t2, h2 = remove_amplitude_zero(t2,h2)

  if( (t1[-1] - t1[0]) < (t2[-1] - t2[0]) ):
    raise ValueError('first waveform should be longer')


  deltaT, deltaPhi, t1, h1 = discrete_minimization_from_discrete_waveforms(t1,h1,t2,h2)

  common_times, t_start, t_end, common_dt = create_common_time_grid(t1,t2,t_low_adj,t_up_adj)

  # fill_value and bounds_error setup such that interpolating outside of the 
  # time grid returns 0 (ie no prediction)
  h1_interp = interp1d(t1,h1,fill_value=(0., 0.), bounds_error=False)
  h2_interp = interp1d(t2,h2,fill_value=(0., 0.), bounds_error=False)

  h2_eval = h2_interp(common_times)

  if(verbose):
    common_times_full = np.arange(t_start,t_end,common_dt)
    h2_eval_full_nrm  = mynorm(h2_interp(common_times_full),1.0)
    h2_eval_nrm       = mynorm(h2_interp(common_times),1.0)
    print("|| h_full || /  || h_adjmynorm(h2_eval_full) = ",h2_eval_full_nrm/h2_eval_nrm)

  return h1_interp, h2_eval, common_times, deltaT, deltaPhi


def minimize_waveform_match(h1_parameterized,href,mynorm,start_values,method):
  """ write me: should pass vector of values to h1... will generalize """
  
  ParameterizedNorm = generate_parameterized_norm(h1_parameterized,href,mynorm)
  
  opt_result   = minimize(ParameterizedNorm, start_values, method=method,tol=1e-12)
  opt_solution = opt_result.x
  
  min_norm     = ParameterizedNorm(opt_solution) # norm's value at global minimum
  h1_align     = h1_parameterized(opt_solution) # h1 waveform optimally matched to href
  guessed_norm = ParameterizedNorm(start_values) # norm's value using initial guess
  
  return [guessed_norm,min_norm], opt_solution, h1_align


def minimize_norm_error(t1,h1,tref,href,mynorm,t_low_adj=.1,t_up_adj=.1,method='nelder-mead',verbose=False):
  """
  Input
  ===== 
  t1,h1:      time/waveform vectors sampled at equally spaced times
  tref,href:  a pair of reference time/waveform vectors
  mynorm:     norm function (e.g. euclidean_norm_sqrd(f,dx) ) which takes a vector f
  t_low,t_up: adjusments  to "clip" the start and end portions of the reference waveform.
              This is useful when the h1 and href durations are very similar in size
              so href need to be restricted a bit to allow the h1 wavefor to "slide" 
              over it.

  Output
  ====== 
  guessed:      relative norm error with discrete "guess" for tc and phic offsets 
  min_norm:     minimized norm error by solving optimization problem
  tc, phic:     time/phase offsets which solve the 2D minimization problem
  common_times: Common time grid on which the minimization problem was solved
  h1_align:     h1 waveform matched to href
  href_eval:    href_eval(common_times) ~ h1_align(common_times)

  Output in form [guessed, min_norm]  [tc, phic]  [common_times, h1_align, href_eval]


  Input expectations
  ================== 
  (i)  t1 and tref should be equally spaced grid of times. But the dt's need not be the same. 
       For different dt's, the common time grid's dt = min( dt_1, dt_ref)
  (ii) for waveforms of different length, (t1,h1) pair should be longer

  Output caveats
  ============== 
  (i) evaluating the norm with values of (tc,phic) might give slightly different answers
      depending on the order of shifts/interpolants etc."""

  ### from discrete waveform data (t1,h1) and (tref,href), return items needed to solve minimization problem ###
  h1_interp, href_eval, common_times, deltaT, deltaPhi = \
      setup_minimization_from_discrete_waveforms(t1,h1,tref,href,t_low_adj,t_up_adj,verbose)
  
  ### h1_parameterized returns evaluations at common_times for given (tc,phic), induces parameterized norm ###
  h1_parameterized  = generate_parameterize_waveform(common_times,h1_interp,'interp1d')
  
  [guessed_norm,min_norm], opt_solution, h1_align = minimize_waveform_match(h1_parameterized,href_eval,mynorm,[0.0,0.0],method)
  
  tc         = opt_solution[0] + deltaT
  phic       = opt_solution[1] + deltaPhi
  
  return [guessed_norm, min_norm], [tc, phic], [common_times, h1_align, href_eval]


def minimize_norm_error_multi_mode(t1,h1,tref,href,mode_list,ell_m_match,t_low_adj=.1,t_up_adj=.1,method='nelder-mead',verbose=False):
  """ performs single-mode match for ell m set in ell_m_match. Uses optimal match parameters 
  for multi-mode waveform alignment.

  Input
  ===== 
  t1,h1:       time/waveform vectors sampled at equally spaced times. h1 can be an
               array or dictionary of modes
  tref,href:   a pair of reference time/waveform vectors. href can be an
               array or dictionary of modes
  mode_list:   list of (ell,m) modes that match the ordering of the modes 
               in h1 and href. If h1 and href are dictionaries, this should be 
               set to None
  ell_m_match: tuple (ell,m) to use for single mode match. Single mode results
               are used to time and phase shift multi-mode waveform
  t_low,t_up:  adjusments  to "clip" the start and end portions of the reference waveform.
               This is useful when the h1 and href durations are very similar in size
               so href need to be restricted a bit to allow the h1 wavefor to "slide" 
               over it.

  Output
  ====== 
  WRITE ME


  Input expectations
  ================== 
  (i)  t1 and tref should be equally spaced grid of times. But the dt's need not be the same. 
       For different dt's, the common time grid's dt = min( dt_1, dt_ref)
  (ii) for waveforms of different length, (t1,h1) pair should be longer

  Output caveats
  ============== 
  (i) evaluating the norm with values of (tc,phic) might give slightly different answers
      depending on the order of shifts/interpolants etc.

  (ii) If m_match is even; odd-m modes might be off by a sign (-1)^m do to physical rotation of
  pi about the z-axis (defined here to parallel to the orbital angular momentum vector). So a final
  alignment is done before modes are returned
  """


  # convert dictionary to list if necessary
  input_dict = False
  assert( type(href) is type(h1) )
  if mode_list is None:
    assert( isinstance(href,dict) )
    mode_list_h1, h1 = modes_dict_to_list(h1)
    mode_list_href, href = modes_dict_to_list(href, mode_list_h1)
    mode_list = mode_list_h1
    input_dict = True
  else:
    assert( isinstance(href,np.ndarray) )

  ### solve single mode match here ###
  ell_match = ell_m_match[0]
  m_match   = ell_m_match[1]
  mode_indx = int(mode_list.index((ell_match,m_match)))
  h_ref_22 = href[:,mode_indx]
  h1_22    = h1[:,mode_indx]
  
  [guessed_norm_1mode, minimized_norm_1mode], [tc, phic], [common_times,h1_align,href_align] = \
    minimize_norm_error(t1,h1_22,tref,h_ref_22,euclidean_norm_sqrd,t_low_adj,t_up_adj,method='nelder-mead')
  z_rot_opt = -phic/m_match
  
  ### use single mode results to time and phase shift multi-mode waveform ###
  h_sphere = h_sphere_builder(mode_list,href.real,href.imag,tref)
  href_eval_hp, href_eval_hc    = h_sphere(common_times)
  href_eval = href_eval_hp + 1.0j*href_eval_hc

  h_sphere = h_sphere_builder(mode_list,h1.real,h1.imag,t1)
  h1_align_hp, h1_align_hc  = h_sphere(times=common_times+tc,z_rot=z_rot_opt)
  h1_align = h1_align_hp + 1.0j*h1_align_hc
  
  h_diff = href_eval - h1_align
  min_norm_sphere = euclidean_norm_sqrd_2sphere(h_diff,1.0)/euclidean_norm_sqrd_2sphere(href_eval,1.0)

  ### check multi-mode waveform's closeness ###
  if m_match%2 == 0: # another rotation by pi might improve odd m modes
    z_rot_opt_pi = z_rot_opt+np.pi
    h1_align_hp_pi, h1_align_hc_pi  = h_sphere(times=common_times+tc,z_rot=z_rot_opt_pi)
    h1_align_pi = h1_align_hp_pi + 1.0j*h1_align_hc_pi
    h_diff_pi = href_eval - h1_align_pi
    min_norm_sphere_pi = euclidean_norm_sqrd_2sphere(h_diff_pi,1.0)/euclidean_norm_sqrd_2sphere(href_eval,1.0)
    #print(min_norm_sphere)
    #print(min_norm_sphere_pi)

    if min_norm_sphere_pi < min_norm_sphere:
      print("Performing a physical rotation by pi...")
      h1_align = h1_align_pi
      min_norm_sphere = min_norm_sphere_pi

  ### compute errors mode-by-mode ###
  rel_mode_errors = compute_many_mode_errors(h1_align,href_eval,mode_list,euclidean_norm_sqrd)

  ### convert output back to dictionary if necessary ###
  if input_dict:
    h1_align  = modes_list_to_dict(mode_list, h1_align)
    href_eval = modes_list_to_dict(mode_list, href_eval)
  
  return [rel_mode_errors, min_norm_sphere], [tc, z_rot_opt], [common_times,h1_align,href_eval]


def h_sphere_builder(modes,hp,hc,t):
  """Returns a function h(t,theta,phi;z_rot,tc). This function can be evaluated 
     for rotations about z-axis and returns either (i) a list of modes or (ii) 
     evaluation on sphere at (theta, phi)

      INPUT
      =====
      modes --- array of modes (ell,m)
      hp/hc --- matrix modes. each column is a mode evaluation for (ell[i],m[i]) in modes
      t     --- arrary of times at which modes have been evaluated"""

  from .harmonics import sYlm as sYlm
  from scipy.interpolate import splrep
  from scipy.interpolate import splev

  ### fill dictionary with model's modes as a spline ###
  hp_modes_spline = dict()
  hc_modes_spline = dict()
  ii = 0
  for ell_m in modes:
    hp_modes_spline[ell_m] = splrep(t, hp[:,ii], k=3)
    hc_modes_spline[ell_m] = splrep(t, hc[:,ii], k=3)
    ii += 1

  ### time interval for valid evaluations ###
  t_min = t.min()
  t_max = t.max()

  ### create function which can be used to evaluate for h(t,theta,phi) ###
  def h_sphere(times,theta=None,phi=None,z_rot=None,psi_rot=None):
    """ evaluations h(t,theta,phi), defined as matrix of modes, or sphere evaluations.

        INPUT
        =====
        times     --- numpy array of times to evaluate at
        theta/phi --- angle on the sphere, evaluations after z-axis rotation
        z_rot     --- rotation angle about the z-axis (coalescence angle)
        psi_rot   --- overall phase adjustment of exp(1.0j*psi_rot) mixing h+,hx"""

    # TODO: restore this after testing
    #if times.min() < t_min or times.max() > t_max:
    #  raise ValueError('surrogate cannot be evaluated outside of its time window')

    if psi_rot is not None:
      raise ValueError('not coded yet')

    ### output will be h (if theta,phi specified) or hp_modes, hc_modes ###
    if theta is not None and phi is not None:
      h = np.zeros((times.shape[0],),dtype=complex)
    else:
      hp_modes = np.zeros((times.shape[0],len(modes)))
      hc_modes = np.zeros((times.shape[0],len(modes)))

    ### evaluate modes at times ###
    jj=0
    for ell_m in modes:

      hp_modes_eval = splev(times, hp_modes_spline[ell_m])
      hc_modes_eval = splev(times, hc_modes_spline[ell_m])

      ### apply rotation about z axis and evaluation on sphere if requested ###
      h_modes_eval  = hp_modes_eval + 1.0j*hc_modes_eval
      if z_rot is not None:
        #print("z rot is %f, rotation by %f"%(z_rot,ell_m[1]))
        h_modes_eval = modify_phase(h_modes_eval,z_rot*ell_m[1])

      if theta is not None and phi is not None:
        sYlm_value =  sYlm(-2,ll=ell_m[0],mm=ell_m[1],theta=theta,phi=phi)
        h = h + sYlm_value*h_modes_eval

      else:
        hp_modes[:,jj] = h_modes_eval.real
        hc_modes[:,jj] = h_modes_eval.imag

      jj+=1

    if theta is not None and phi is not None:
      return h.real, h.imag
    else:
      return hp_modes, hc_modes

  return h_sphere


def compute_many_mode_errors(h,h_ref,mode_list,mynorm):
  """input: matrix of modes h, h_ref, mode_list, and norm 
    output: dictionary relating mode to relative errors h_{ell,m} compared with href_{ell,m} """

  h_mode_diff = h_ref - h
  relative_mode_errs = dict()
  ii=0
  for ell_m in mode_list:
    err = mynorm(h_mode_diff[:,ii],1.0)/mynorm(h_ref[:,ii],1.0)
    relative_mode_errs[ell_m] = err
    ii += 1

  return relative_mode_errs


def interpolant_h(t, h, deg=3, s=None):
  """Compute spline interpolant of input data h at samples t.

  s is the spline smoothing parameter

  """
  
  from scipy.interpolate import splrep
  from scipy.interpolate import splev
  dtype = h.dtype
  if dtype == 'complex':
    interp_real = splrep(t, np.real(h), k=deg, s=s)
    interp_imag = splrep(t, np.imag(h), k=deg, s=s)
    return interp_real, interp_imag
  elif dtype == 'double':
    interp = splrep(t, h, k=deg, s=s)
    return interp
  else:
    raise Exception("Function to be interpolated must be real or complex.")
  pass


def interpolate_h(tin, h, tout, deg=3, s=None):
  """Interpolate input data h at samples tout.

  s is the spline smooth parameter

  """

  from scipy.interpolate import splrep
  from scipy.interpolate import splev
  
  if tout[0] < tin[0] or tout[-1] > tin[-1]:
    print(">>> Warning: Requested samples are outside of interpolated domain.")
  
  dtype = h.dtype
  if dtype == 'complex':
    interp_real, interp_imag = interpolant_h(tin, h, deg=deg,s=s)
    return splev(tout, interp_real) + 1j*splev(tout, interp_imag)
  elif dtype == 'double':
    interp = interpolant_h(tin, h, deg=deg,s=s)
    return splev(tout, interp)
  else:
    raise Exception("Function to be interpolated must be real or complex.")
  pass


def spline_f(tin, h, deg=3, s=None):
  """ Return a function f_sp such that f_sp(t) returns the spline
      evaluation of f"""

  from scipy.interpolate import splrep
  from scipy.interpolate import splev

  dtype = h.dtype
  if dtype == 'complex':
    interp_real, interp_imag = interpolant_h(tin, h, deg=deg, s=s)
  elif dtype == 'double':
    interp = interpolant_h(tin, h, deg=deg, s=s)
  else:
    raise Exception("Function to be interpolated must be real or complex.")

  def f_sp(t):
    if type(t) == float or type(t) == int or type(t) == np.float64:
      if t < tin[0] or t > tin[-1]:
        print(">>> Warning: Requested sample value %f is outside of interpolated domain."%t)
    else:
      if t[0] < tin[0] or t[-1] > tin[-1]:
        print(">>> Warning: Requested samples are outside of interpolated domain.")

    if dtype == 'complex':
      return splev(t, interp_real) + 1j*splev(t, interp_imag)
    elif dtype == 'double':
      return splev(t, interp)

  return f_sp


def energy_flux_from_modes(h, time, q, M=1., tend=100.):
  """ Computes the radiated energy and flux from each mode (E_modes), and 
    total energy (E_tot) as described in Eq.(2) of arXiv:1802.04276v2 and E0_over_M (Eq. 3). 
        
    We assume equal contributions from m>0 and m<0 modes, 
    which is only true for binary systems that orbit in the x-y plane.
        
    INPUT
    =====
    h:  The complex gravitational strain as a dictionary of modes.
        Example: h[(2,2)] is an numpy array
    time: A numpy array, times at which the gravitational strain is calculated.
    M:    Total mass of the binary at the begining of the evolution. Default: 1.0 
    tend: compute up to this final time (in units of M)

    RETURNS
    =====
    E: A dictionary which contains...
      (1) E['total'], the total radiated energy by graviational waves over different modes. This 
          Does not include a PN estimated value E0_over_M for flux at E(0)
      (2) E[(l, m)] the total energy radiated that does include a PN estimated value E0_over_M for flux at E(0)


    EXAMPLE
    =======
    # load model
    import gwsurrogate as gws
    model = gws.LoadSurrogate("NRHybSur3dq8")

    # import routine
    from gwtools.gwtools import energy_flux_from_modes

    # evaluate model
    q=2.0
    times, h, dynamics = model(q=q,chiA0=[0,0,0],chiB0=[0,0,0], dt=0.1, units='dimensionless', f_low=.005)

    # Compute flux
    E_fluxes = energy_flux_from_modes(h=h, time=times, q=q, M=1., tend=100)

    # plot flux
    import matplotlib.pyplot as plt
    plt.plot(times, E_fluxes['total'],'black',label='total energy flux')
    plt.plot(times, E_fluxes[(2,2)],'blue',label='energy flux from 22 mode only')
    plt.plot(times, E_fluxes[(2,-2)],'r--',label='energy flux from 22 mode only')
    plt.legend()
           
           
    NOTE
    ====
    After this code was written, it was realized that similar code is alredy online: 

           https://github.com/dgerosa/surrkick

    Future work: directly compare this code to the one above (see https://github.com/dgerosa/surrkick/blob/master/surrkick/surrkick.py#L283)

    Author: Estuti Shukla
    Date: 9/10/2021
  """
    
  # Final time in units of M
  tend=tend*M

  #finite differences
  hdot={j:np.gradient(h[j],edge_order=2)/np.gradient(time,edge_order=2) for j in h.keys()}

  #from surkick model code https://github.com/dgerosa/surrkick/blob/master/surrkick/surrkick.py
  #hdot=  {k: spline(time,v.real).derivative()(time)+1j*spline(time,v.imag).derivative()(time) for k, v in h.items()}

  dEdt={'total':0}

  for i in h.keys():
    (l,m)=i
    #ensures that m >=0 to avoid any error in calculation. m<0 are redundant in this case of orbital symmetry and already accouted for in the calcualtions below.
    assert(m>=0),"Negative value of m" 
    dEdt[i]=(1/(16*np.pi))*(np.abs(hdot[i])**2) # dEdt using the equation 2 of  arXiv:1802.04276v2
    if m!=0:
      # multiplied by 2 to account for both positive and negative modes  
      dEdt['total']+=dEdt[i]*2
      dEdt[(l,-m)] = dEdt[i]
    else:
      dEdt['total']+=dEdt[i]

  E={}
  for j in dEdt.keys():
    #from surkick model code https://github.com/dgerosa/surrkick/blob/master/surrkick/surrkick.py
    #E[j]=spline(time,dEdt[j]).antiderivative()(time)

    #E[j]=sp.cumtrapz(dEdt[j],time)
    E[j]=sp.cumtrapz(dEdt[j],time,initial=0.0)
    #print(E[j].shape)
    #print(dEdt[j].shape)
    #print(time.shape)

  tf=time[0]+tend
  time1=time[time<tf]
  #from surkick model code https://github.com/dgerosa/surrkick/blob/master/surrkick/surrkick.py
  #Edot0=spline(time[time<tf],dEdt['total'][time<tf]).antiderivative()(time1[-1])/((time1[-1]-time1[0])*M)


  Edot0=sp.trapz(dEdt['total'][0:len(time1)],time1)/((time1[-1]-time1[0])*M)
  E0_over_M=((5./1024.)*((q**3.)/(1.+q)**6.)*Edot0)**(1./5.)  #A float type number as described by eq 3. in arXiv:1802.04276v2.

  E['total']+=E0_over_M*M

  return E



def bondi_mass_binary(E, M=1.):
  """ Computes Bondi mass as described in Eq.(4) of arXiv:1802.04276v2. Returns M_t as an array. 

  INPUT
  =====
  E: An dictionary which contains the energy radiated over
  all the modes (as well as the total energy) by the gravitational wave.
  M: Total mass of the binary at the begining of the evolution. Default: 1.0 

  RETURNS
  =====
  M_t: An array which defines the time-dependent (Bondi) mass of the binary.
  M_rem_over_M: A float point number which is the remnant mass or the mass of the post-merger 
               of BH in units of the mass at early times. Shown in eq.5 of arXiv:1802.04276v2. 
                
  Author: Estuti Shukla
  Date: 9/10/2021

  """

  M_t=M+E['total'][0]-E['total']

  #final mass in units of the mass at early times (t->-infinity)
  M_rem_over_M=1-E['total'][-1]/(1+E['total'][0])

  return M_t, M_rem_over_M


##############################################
# Convenient interfaces for LALsim functions #
##############################################

def aLIGOZeroDetHighPower(freqs):
  """ Compute the ZeroDetHighPower PSD on a numpy array f"""

  import lalsimulation as LS
  psd = []
  for f in freqs:
    psd.append(LS.SimNoisePSDaLIGOZeroDetHighPower(f))
  psd = np.array(psd)
  return psd

#def EOBNRv2_LAL(Mtot,q,dt,fmin,Dist,inclination):
#    """ Dist in megaparsecs"""
#    
#    Dist = Dist * 1e6 * PC_SI
#    M1,M2  = gwtools.Mq_to_m1m2(Mtot,q)
#    hp, hc = lalsim.SimInspiralChooseTDWaveform(phiRef=0.0,deltaT=dt,m1=M1,m2=M2,s1x=0.0,s1y=0.0,s1z=0.0,\
#                                                s2x=0.0,s2y=0.0,s2z=0.0,f_min=fmin,f_ref=0.0,\
#                                                r=Dist,i=inclination,lambda1=0.0,lambda2=0.0,\
#                                                waveFlags=None,nonGRparams=None,amplitudeO=0,phaseO=7,\
#                                                approximant=lalsim.EOBNRv2)
#    h      = hp.data.data + (1j)*hc.data.data
#    times  = np.arange(np.size(hp.data.data))*hp.deltaT
#    
#    times,h = gwtools.remove_amplitude_zero(times,h) # removes end portion of waveform which is zero
#    
#    return times, h


def EOBNRv2_LAL(Mtot,q,dt,fmin,Dist,inclination):
  """ Simplified interface to EOBNRv2 (dominant mode). Dist in megaparsecs"""

  from lalsimulation import SimIMREOBNRv2DominantMode

  Dist = Dist * 1e6 * PC_SI
  Mtot = Mtot * MSUN_SI

  M1,M2 = Mq_to_m1m2(Mtot,q)
    
  hp, hc = SimIMREOBNRv2DominantMode(phiC=0.0,deltaT=dt,m1SI=M1,m2SI=M2,\
                                     fLower=fmin,distance=Dist,inclination=inclination)
    
  h        = hp.data.data + (1j)*hc.data.data
  times    = np.arange(np.size(hp.data.data))*hp.deltaT
  times, h = remove_amplitude_zero(times,h) # removes end portion of waveform which is zero
    
  return times, h


def generate_LAL_modes(approximant,q, chiA0, chiB0, dt, M,
    dist_mpc, f_low, f_ref=20, phi_ref=0.0, ellMax=None, \
    unlimited_extrapolation=False):
  """ Returns a dictionary of modes and array of times.
      
      INPUT
      =====
      approximant -- Model used (ex. lalsim.EOBNRv2)
      q           -- Mass Ratio (M1/M2)
      chiA0       -- Spin of black hole 1 ([S1x,S1y,S1z] dimensionless)
      chiB0       -- Spin of black hole 2 ([S2x,S2y,S2z] dimensionless)
      dt          -- Waveform sampling (s)
      M           -- Mass in Solar Masses
      dist_mpc    -- Distance in MegaParsecs
      f_low       -- Lowest/Starting frequency (Hz)
      f_ref       -- Frequency value, arbitrary (Hz)
      phi_ref     -- Phi at f_ref (radians)


  Note: The first version of this routine was written by Vijay Varma
        for the NR surrogate (q=4) code review. """  
  import lalsimulation as lalsim
  import lal
  import numpy as np
  
  distance = dist_mpc* 1.0e6 * lal.PC_SI
  
  m1_kg =  M*lal.MSUN_SI*q/(1.+q)
  m2_kg =  M*lal.MSUN_SI/(1.+q)
  
  dictParams = lal.CreateDict()
  if unlimited_extrapolation:
      lal.DictInsertUINT4Value(dictParams, "unlimited_extrapolation", 1)
      
      if ellMax is not None:
        ma=lalsim.SimInspiralCreateModeArray()
        for ell in range(2, ellMax+1):
            lalsim.SimInspiralModeArrayActivateAllModesAtL(ma, ell)
        lalsim.SimInspiralWaveformParamsInsertModeArray(dictParams, ma)
  
  lmax = 5    # This in unused
  hmodes = lalsim.SimInspiralChooseTDModes(phi_ref, dt, m1_kg, m2_kg,chiA0[0],
                    chiA0[1], chiA0[2], chiB0[0], chiB0[1],chiB0[2],f_low,
                    f_ref, distance, dictParams, lmax, approximant)
  
  t = np.arange(len(hmodes.mode.data.data)) * dt
  mode_dict = {}
  while hmodes is not None:
        mode_dict['h_l%dm%d'%(hmodes.l, hmodes.m)] = hmodes.mode.data.data
        hmodes = hmodes.next
  return t, mode_dict


def fft_timeseries(h,df=0.0,verbose=False):
  """ Take an FFT of LAL datatype REAL8 or COMPLEX16 TimeSeries

      This routine was originally written by Evan Ochsner for lalsimwaves.py

     INPUT
     =====
     h -- time-series (e.g. strain hp*Fp + hc+Fc). h must be a REAL8TimeSeries
          which, for example, results from add hp and hc as returned 
          from  hp, hc = lalsim.SimInspiralChooseTDWaveform(...
     df     -- Setting df=0 means the TD waveform will just pads to the next power of 2.
               For df!=0, the TD waveform will be padded further, or it will print a
               warning if the waveform is so long that it requires a smaller df. """

  # to determine if h is real or complex timeseries
  from lal import REAL8TimeSeries, COMPLEX16TimeSeries
  assert(type(h)==REAL8TimeSeries or type(h)==COMPLEX16TimeSeries)

  from lal import ResizeREAL8TimeSeries, ResizeCOMPLEX16TimeSeries,\
                  CreateForwardREAL8FFTPlan, CreateForwardCOMPLEX16FFTPlan,\
                  REAL8TimeFreqFFT, COMPLEX16TimeFreqFFT,\
                  CreateCOMPLEX16FrequencySeries, HertzUnit

  sample = 1.0/h.deltaT # The sample rate

  print("sample rate = %f"%sample)

  # Find next power of 2 length #
  padlen = 1
  while padlen < h.data.length:
    padlen *= 2

  print("padlen (old) = %f"%padlen)
  # If df=0, use above padlen. If df != 0, then we... #
  if df != 0:
    # Check if padlen gives smaller df than requested
    # If so, print warning and use padlen
    if padlen > int(sample/df):
      print("Warning: waveform too long for requested df =", df)
      print("Instead using df =",  sample/padlen)  # padlen/sample
    # If requested df is finer freq. binning, then pad further
    if padlen < int(sample/df):
      padlen = int(sample/df)

  print("padlen (new) = %f"%padlen)

  # Pad h and create fft plan
  if (type(h) == REAL8TimeSeries):
    ResizeREAL8TimeSeries(h, 0, padlen)
    plan = CreateForwardREAL8FFTPlan(padlen, 0)
    hoff = CreateCOMPLEX16FrequencySeries(name="FD hplus",epoch=h.epoch,f0=0,\
                                          deltaF=1./(h.deltaT/h.data.length),\
                                          sampleUnits=HertzUnit,\
                                          length=int(padlen/2+1))
    REAL8TimeFreqFFT(hoff, h, plan)
  elif (type(h) == COMPLEX16TimeSeries):
    ResizeCOMPLEX16TimeSeries(h, 0, padlen)
    plan = CreateForwardCOMPLEX16FFTPlan(padlen,0)
    hoff = CreateCOMPLEX16FrequencySeries(name="FD hp+ihc",epoch=h.epoch,f0=0,\
                                        deltaF=1./(h.deltaT/h.data.length),\
                                        sampleUnits=HertzUnit,\
                                        length=padlen) #len OK?
    COMPLEX16TimeFreqFFT(hoff, h, plan)

  # deduce frequencies f such that (f,hoff(f))
  TDlen  = padlen
  FDlen  = int( hoff.data.length )
  siglen = TDlen*h.deltaT

  deltaF = 1/siglen
  frqs   = np.arange(FDlen) * deltaF
  if( type(h) == COMPLEX16TimeSeries):
    frqs = frqs - (sample/2.0)

  if verbose:
    print('TDlen = ',TDlen)
    print('TDlen/2 + 1 = ',TDlen/2+1)
    print('FDlen = ',FDlen)
    print('TDlen*dt = ',siglen)
    
  return frqs, hoff


def REAL8_TAPER_from_numpy(h,dt,sampleUnits,taper):
  """ From real timeseries h and deltaT dt, create a REAL8TimeSeries
      object and taper. 

      INPUT
      =====
      h           --- a real-valued numpy array representing the timeseries
      dt          --- time interval between samples
      sampleUnits --- lal.XXX units tag (e.g. lal.SecondUnit)
      taper       --- lalsim.XXX taper tag (e.g. lalsim.SIM_INSPIRAL_TAPER_STARTEND)"""

  from lal import CreateREAL8TimeSeries
  from lalsimulation import SimInspiralREAL8WaveTaper

  h_REAL8 = CreateREAL8TimeSeries("h(t)",epoch=0.0,f0=0.0,deltaT=dt,\
                                  sampleUnits=sampleUnits,length=len(h))
  h_REAL8.data.data[:] = h[:]

  SimInspiralREAL8WaveTaper(h_REAL8.data, taper)

  return h_REAL8


def COMPLEX16_TAPER_from_numpy(h,dt,sampleUnits,taper):
  """ From complex timeseries h and deltaT dt, create a Complex16TimeSeries
      object and taper. 

      INPUT
      =====
      h           --- a complex-valued numpy array representing the timeseries
      dt          --- time interval between samples
      sampleUnits --- lal.XXX units tag (e.g. lal.SecondUnit)
      taper       --- lalsim.XXX taper tag (e.g. lalsim.SIM_INSPIRAL_TAPER_STARTEND)"""

  from lal import CreateCOMPLEX16TimeSeries
  from lalsimulation import SIM_INSPIRAL_TAPER_NONE

  # LAL complex taper routine (~ SimInspiralCOMPLEX16WaveTaper) doesn't exist
  assert(taper==SIM_INSPIRAL_TAPER_NONE)

  h_COMPLEX16 = CreateCOMPLEX16TimeSeries("hp+ihc",epoch=0.0,f0=0,deltaT=dt,\
                                          sampleUnits=sampleUnits,length=len(h))
  h_COMPLEX16.data.data = h[:]

  return h_COMPLEX16


# TODO: should have set of routines which use numpy fft.fft (see Jonathan's code)
def fft_from_numpy(h,dt,sampleUnits,taper,df=0):
  """ From real or complex timeseries, h, and deltaT, dt, taper and
      perform an FFT using LAL code.

      INPUT
      =====
      h           --- a real or complex valued numpy array representing the timeseries
      dt          --- time interval between samples
      sampleUnits --- lal.XXX units tag (e.g. lal.SecondUnit)
      taper       --- lalsim.XXX taper tag (e.g. lalsim.SIM_INSPIRAL_TAPER_STARTEND).
                      To use a non-LAL taper, taper before passing h to this routine
                      and set taper = lalsim.SIM_INSPIRAL_TAPER_NONE

      OUTPUT
      ======
      hf --- FFT as a LAL timeseries (COMPLEX16FrequencySeries)"""


  # Taper before padding (could modify ringdown, which maybe good to do)
  if(h.dtype == np.double):
    h_REAL8  = REAL8_TAPER_from_numpy(h,dt,sampleUnits=sampleUnits,taper=taper)
    frqs, hf = fft_timeseries(h_REAL8,df,False)
  elif(h.dtype == np.complex):
    h_COMPLEX16 = COMPLEX16_TAPER_from_numpy(h,dt,sampleUnits,taper)
    frqs, hf = fft_timeseries(h_COMPLEX16,df,False)
  else:
    raise ValueError('dtype not supported')

  return frqs, hf


def convert_COMPLEX16FrequencySeries_to_2Sided_numpy(h,freqs):
  """ convert a lal data type COMPLEX16FrequencySeries, which stores a 1-sided 
      fft, to a 2-sided fft result a numpy array."""

  N = freqs.size
  hf_numpy   = np.array([h.data.data[N-i-1] if i<N else h.data.data[i-N+1] for i in np.arange((N-1)*2) ],dtype=complex)
  fs_2_sided = np.array([-freqs[N-i-1] if i<N else fs[i-N+1] for i in np.arange((N-1)*2) ])

  return fs_2_sided, hf_numpy


def make_psd_np_array(psd,freq_pts):
  """ Evaluate a canned LAL PSD at array of frequency points.

     INPUT
     =====
     psd      --- lalsimulation.SimNoisePSDXXX function 
     freq_pts --- array of frequency points """

  return np.array([ psd(f) for f in freq_pts],dtype=complex)


def whiten_numpy_waveform(psd,wv,freq_pts):
  """ Return whitened waveform h(f) / sqrt(S(f)) as a numpy array.

    INPUT
    =====
    psd      --- lalsimulation.SimNoisePSDXXX function
    wv       --- complex FFT waveform data (numpy array)
    freq_pts --- numpy array of frequency points """

  assert(len(wv) == len(freq_pts))
  return np.array([ wv[i] / np.sqrt( psd(freq_pts[i]) ) for i in np.arange(freq_pts.size)],dtype=complex,copy=True)


def whiten_COMPLEX16_waveform(psd,wv,freq_pts):
  """  Whiten a COMPLEX16 waveform  in place.

    INPUT
    =====
    psd --- lalsimulation.SimNoisePSDXXX function
    wv  --- complex FFT waveform data
    freq_pts --- numpy array of frequency points """

  wv_data = np.array(wv.data.data[:],dtype=complex)
  assert(len(wv_data) == len(freq_pts))
  wv.data.data[:]  = whiten_numpy_waveform(psd,wv_data,freq_pts)


def Fplus(theta, phi, psi):
  """
  "plus" antenna pattern function of sky location and polarization angle
  """
  return 0.5*(1. + np.cos(theta)**2)*np.cos(2.*phi)*np.cos(2.*psi) - np.cos(theta)*np.sin(2.*
phi)*np.sin(2.*psi)


def Fcross(theta, phi, psi):
  """
  "cross" antenna pattern function of sky location and polarization angle
  """
  return 0.5*(1. + np.cos(theta)**2)*np.cos(2.*phi)*np.sin(2.*psi) + np.cos(theta)*np.sin(2.*
phi)*np.cos(2.*psi)


def find_fft_deltaF(times):
  """Find an FFT-appropriate deltaF from array of times"""
  T = times.max() - times.min()
  powof2 = 1.0
  while( powof2 < T ):
      powof2 = powof2*2.0
      
  deltaF = 1.0/powof2
  print("Next power of 2 = %i"%powof2)
  print("DeltaF is %f"%deltaF)

  return deltaF


##############################################
# Functions for changing data representation
# of multi-mode waveforms dictionary <-> list
##############################################


def modes_dict_to_list(mode_dict, mode_list=None):
  """ Convert a dictionary of modes into a list of modes whose elements 
  are numpy vectors (the time series). 

  If an array of modes is given, the returned mode_list list will have exactly 
  that ordering. 
  """

  if mode_list is None:
    mode_list = []
    i=0
    for k,v in mode_dict.items():
      mode_list.append(k)
      i = i + 1
  else:
    for mode in mode_list:
      assert(mode in list(mode_dict.keys())) 

  mode_array = np.zeros((len(list(mode_dict.values())[0]),len(mode_list)),dtype=np.complex)
  i=0
  for mode in mode_list:
    mode_array[:,i] = mode_dict[mode]
    i = i + 1

  return mode_list, mode_array

def modes_list_to_dict(mode_list, mode_array):
  """ Convert a numpy array indexed by list of modes into a dictionary
  of modes. 

  Assumes elements of mode_list can be used as a dictionary hash.

     Ex: mode_list = [(2,2), (3,3)]
         h[0,:]  -> 22 mode
         h[1,:]  -> 33 mode

  """

  if (mode_array.shape[0] < mode_array.shape[1]):
  	  flipped = True
  else:
  	  flipped = False

  mode_dict = {}
  for i, mode in enumerate(mode_list):
    #print(type(mode))
    #print(mode)
    #print(type(mode_array))
    #print(type(i))
    if not flipped:
    	mode_dict[mode] = mode_array[:,i]
    else:
        mode_dict[mode] = mode_array[i,:]
  return mode_dict
