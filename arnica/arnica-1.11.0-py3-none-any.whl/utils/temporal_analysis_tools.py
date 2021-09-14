import numpy as np
import matplotlib
from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
import scipy.stats as stats
import satis.temporal_analysis_tool as tat
import warnings


def resample_signal(time, signal, dtime=None):
    """
	*Resample the initial signal at a constant time interval.*
  
	:param time: Time vector of your signal
	:param signal: Signal vector
	:dtime: New time step
	:returns:            
	- **rescaled_time** - Uniformally rescaled time vector
	- **rescaled_signal** - Rescaled signal

	.. note:: 	If a dtime is given, the interpolation is made to 
				have a signal with a time interval of dtime.
				Else, the dt is the smallest time interval between
				two values of the signal.
	"""

    warnings.warn(("Prefer the satis.temporal_analysis_tool function"),
                  DeprecationWarning)
    rescaled_time, rescaled_signal = tat.resample_signal(time, signal, dtime)

    return rescaled_time, rescaled_signal


def calc_autocorrelation_time(time, signal, threshold=0.2):
    """
	*Estimate the autocorrelation time at a given threshold.*
	
	:param time: Time vector of your signal
	:param signal: Signal vector
	:param threshold: Threshold under which the signal is correlated
	:type threshold: float

	:returns:

	- **autocorrelation_time** - Minimum time step to capture the signal at a
								 correltion under thethreshold
	"""

    warnings.warn(("Prefer the satis.temporal_analysis_tool function"),
                  DeprecationWarning)

    autocorrelation_time = tat.calc_autocorrelation_time(time, signal, threshold)

    return autocorrelation_time


def show_autocorrelation_time(time, signal, threshold=0.2):
    """
	*Plot the autocorrelation function of the signal.*
	
	:param time: Time vector of your signal
	:param signal: Signal vector
	:param threshold: Autocorrelation threshold

	:returns:

	- **fig** - Figure of the result

	"""

    warnings.warn(("Prefer the satis.temporal_analysis_tool function"),
                  DeprecationWarning)

    figout = tat.show_autocorrelation_time(time, signal, threshold)

    return figout


def sort_spectral_power(time, signal):
    """
	*Determine the harmonic power contribution of the signal.*
	
	:param time: Time vector of your signal
	:param signal: Signal vector

	returns:

	- **harmonic_power** - Harmonic power of the signal
	- **total_power** - Total spectral power of the signal


	.. note:: 	It calculates the Power Spectral Density (PSD) of the complete
				signal and of a downsampled version of the signal. The 
				difference of the two PSD contains only harmonic components.
	"""

    warnings.warn(("Prefer the satis.temporal_analysis_tool function"),
                  DeprecationWarning)

    harmonic_power, total_power = tat.sort_spectral_power(time, signal)

    return harmonic_power, total_power


def power_representative_frequency(time, signal, threshold=0.8):
    """
	*Calculate the frequency that captures a level of spectral power.*

	:param time: Time vector of your signal
	:param signal: Signal vector
	:param threshold: Level of representativity of the spectral power

	:returns:

	- **representative_frequency** - Frequency above which the power threshold is reached

	.. note:: 	It calculates the cumulative power spectral density and returns
				the frequency that reaches the threshold of spectral power.
	"""

    warnings.warn(("Prefer the satis.temporal_analysis_tool function"),
                  DeprecationWarning)

    representative_frequency = tat.power_representative_frequency(time, signal, threshold)

    return representative_frequency


def show_power_representative_frequency(time, signal, threshold=0.80):
    """
	*Plot the power spectral density of the signal.*
	
	:param time: Time vector of your signal
	:param signal: Signal vector
	:param threshold: Power representative frequency threshold

	:returns:

	- **fig** - Figure of the result

	"""

    warnings.warn(("Prefer the satis.temporal_analysis_tool function"),
                  DeprecationWarning)

    figout = tat.show_power_representative_frequency(time, signal, threshold)

    return figout


def ks_test_distrib(data, distribution="normal"):
    """
	*Calculate the correlation score of the signal with the distribution*

	:param data: array of values
	:param distribution: kind of distribution the values follow to test

	:returns:

	- **score** -Minimum score over the height of the ks test
	- **position** -Index of the height at which the min. of the test is found
	- **height** -Corresponding heiht where the min. is found
	- **scale** -Scale parameter of the lognormal fitting

	"""
    warnings.warn(("Prefer the satis.temporal_analysis_tool function"),
                  DeprecationWarning)

    score, position, height, scale = tat.ks_test_distrib(data, distribution)

    return score, position, height, scale


def show_temperature_distribution(temperature_recording, height, distribution="normal"):
    """
	*Plot the temperature distribution and the fitting curve*

	:param temperature_recording: Temperature as a function of height and time
	:param height: Height in the plan40
	:param distribution: Type of distribution for the fitting method

	:returns:

	- **fig** - Figure of the result
	"""
    warnings.warn(("Prefer the satis.temporal_analysis_tool function"),
                  DeprecationWarning)

    figout = tat.show_temperature_distribution(temperature_recording, height, distribution)

    return figout


def duration_for_uncertainty(
    time, signal, target=10, confidence=0.95, distribution="normal"
):
    """
	*Give suggestion of simulation duration of a plan40 calculation.*
	
	:param time: Time vector of your signal
	:param signal: Signal vector
	:param target: Desired amplitude of the confidence interval
	:param confidence: Level of confidence of the interval
	:param distribution: Type of distribution of the signal to make the interval

	:returns:

	- **duration** -Duration of the signal
	"""

    warnings.warn(("Prefer the satis.temporal_analysis_tool function"),
                  DeprecationWarning)

    duration = tat.duration_for_uncertainty(time, signal, target, confidence, distribution)

    return duration


def uncertainty_from_duration(
    dtime, sigma, duration, confidence=0.95, distribution="normal"
):
    """
	*Give confidence interval length of a plan40 calculation.*

	:param dtime: Time step of your solutions
	:param sigma: Standard deviation of your signal
	:param duration: Desired duration of the signal
	:param confidence: Level of confidence of the interval
	:param distribution: Type of distribution of the signal to make the interval

	:returns:

	- **length** - Length of the confidence interval in K
	"""

    warnings.warn(("Prefer the satis.temporal_analysis_tool function"),
                  DeprecationWarning)

    length = tat.uncertainty_from_duration(dtime, sigma, duration, confidence, distribution)

    return length


def convergence_cartography(time, signal, **kwargs):
    """
	*Create a cartography of the convergence of the confidence interval in a simulation.*

	:param time: Time vector of your signal
	:param signal: Signal vector


	==**kwargs==
	
		:param max_time: Maximal simulation duration
		:param interlen: Maximal interval length

	:returns:
		- **fig** - Figure of the cartography

	"""
    warnings.warn(("Prefer the satis.temporal_analysis_tool function"),
                  DeprecationWarning)

    fig = tat.convergence_cartography(time, signal, **kwargs)

    return fig


def calculate_std(time, signal, frequency):
    """
	*Give the standard deviation of a signal at a given frequency.*
	
	:param time: Time vector of your signal
	:param signal: Signal vector
	:param frequency: Frequency at which values of the recording are taken

	:returns:

		- **std** - Standard deviation of the values taken from the recording
	"""

    warnings.warn(("Prefer the satis.temporal_analysis_tool function"),
                  DeprecationWarning)

    std = tat.calculate_std(time, signal, frequency)

    return std


def power_spectral_density(time, signal):
    """
	*Automate the computation of the Power Spectral Density of a signal.*

	:param time: Time vector of your signal
	:param signal: Signal vector

	:returns:

	- **frequency** -Frequency vector of the signal's power spectral density
	- **power_spectral_density** -Power spectral density of the signal
	"""

    warnings.warn(("Prefer the satis.temporal_analysis_tool function"),
                  DeprecationWarning)

    frequency, power_spectral_density = tat.power_spectral_density(time, signal)

    return frequency, power_spectral_density


def to_percent(y, position):
    """
	*Rescale the y-axis to per*
    
    """
    warnings.warn(("Prefer the satis.temporal_analysis_tool function"),
                  DeprecationWarning)

    s = tat.to_percent(y, position)

    return s 


def plot_distributions(path="./data.txt"):

    warnings.warn(("Prefer the satis.temporal_analysis_tool function"),
                  DeprecationWarning)

    tat.plot_distributions(path)