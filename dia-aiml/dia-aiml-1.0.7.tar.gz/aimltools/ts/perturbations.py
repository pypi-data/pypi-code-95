"""
Sub-module of TSAnalysis

Contains classes and methods to induce perturbations on signals
"""

import numpy as np
import pandas as pd
from abc import ABCMeta, abstractmethod
from scipy.stats import norm
from aimltools.ts.denoising import denoise
import logging

logger = logging.getLogger(__name__)


# Defines perturbation mixins
class BaseMixin(metaclass = ABCMeta):
    """
    Defines pattern for child mixins
    """

    @abstractmethod
    def perturb_transform(self):
        """Mandatorily implement this method in all child mixins"""

    @abstractmethod
    def perturb_transform_(self):
        """Mandatorily implement this method in all child mixins"""

class SignalTimeDilationMixin(BaseMixin):
    """
    Mixin class for perturbing signal through signal time dilation
    """
    def __init__(self, D):
        self.__D = D
    
    def perturb_transform(self, signal, D):
        if D==1:
            return signal
        else:
            xp = np.arange(len(signal))
            b = int(D * len(signal))
            signal = np.interp(np.linspace(0,len(signal),b), xp, signal)
            return signal

    def perturb_transform_(self, signal):
        return self.perturb_transform(signal, D = self.__D)

class HorizontalShiftMixin(BaseMixin):
    """
    Mixin class for perturbing signal through horizontal shifting
    """
    def __init__(self, S, method):
        self.__S = S
        self.__method = method

    def perturb_transform(self, signal, S, method = 'proportional'):
        
        if method == 'proportional':
            step = round(len(signal) * S)
            
            d = signal[0] - signal[-1]
            start = signal[-step:] + d
            signal = np.concatenate([start,signal[:-step]])
            return signal
        
        if method == 'absolute':
            step = S
            
        d = signal[0] - signal[-1]
        start = signal[-step:] + d
        signal = np.concatenate([start,signal[:-step]])
        return signal

    def perturb_transform_(self, signal):
        return self.perturb_transform(signal, S = self.__S, method = self.__method)

class VerticalShiftMixin(BaseMixin):
    """
    Mixin class for perturbing signal through vertical shifting
    """
    def __init__(self, S, method):
        self.__S = S
        self.__method = method

    def perturb_transform(self, signal, S, method = 'proportional'):
        
        if method == 'proportional':
            amplitude_range = abs(max(signal) - min(signal))
            step = amplitude_range * S
            
        if method == 'absolute':
            step = S
            
        signal = signal + step
        
        return signal

    def perturb_transform_(self, signal):
        return self.perturb_transform(signal, S = self.__S, 
                                        method = self.__method)

class AmplitudeVariationMixin(BaseMixin):
    """
    Mixin class for perturbing signal through amplitude variation
    """
    def __init__(self, A):
        self.__A = A

    def perturb_transform(self, signal, A):
        # Denoise through DWT
        signal, noise = denoise(signal, return_noise=True)
        signal = signal*A + noise
        return signal

    def perturb_transform_(self, signal):
        return self.perturb_transform(signal, A = self.__A)

class GaussianPeakMixin(BaseMixin):
    """
    Mixin class for perturbing signal through Gaussian kernel
    """
    def __init__(self, h, n_peaks="random"):
        self.__h = h
        self.__n_peaks = n_peaks

    def perturb_transform(self, signal, h, n_peaks="random"):
        x_all = np.arange(0, signal.shape[0], 1) 
        A = (max(signal) - min(signal))
        if n_peaks == "random":
            n_peaks = np.random.choice(np.arange(1,6))
        
        for _ in range(n_peaks):
            mean = round(np.random.normal(loc=signal.shape[0]/2, scale=signal.shape[0]/8))
            std = np.random.choice(np.arange(1,4, step=0.1), replace=True)
            y2 = norm.pdf(x_all, mean, std)
            try:
                if signal[mean] < 0:
                    signal = signal - y2*A*h
                else:
                    signal = signal + y2*A*h
            except:
                signal = signal + y2*A*h
            
        return signal

    def perturb_transform_(self, signal):
        return self.perturb_transform(signal, h = self.__h, n_peaks=self.__n_peaks)


class SimplePeakMixin(BaseMixin):
    def __init__(self, h):
        self.__h = h

    def perturb_transform(self, signal, h):
        x_all = np.arange(0, signal.shape[0], 1)
        A = (max(signal) - min(signal))
        y2 = norm.pdf(x_all,signal.shape[0]/2,2)
        signal = signal + y2*A*h
        return signal

    def perturb_transform_(self, signal):
        return self.perturb_transform(signal, h = self.__h)

# Defines base class
class PerturbationBaseClass(metaclass = ABCMeta):
    """"
    Base class containing common functionality and abstract methods
    """
    
    def __init__(self, signal, perturbation_type, **kwargs):
        self.signal = signal
        self.perturbation_type = perturbation_type
        self.kwargs = kwargs

    def __repr__(self):
        return """Perturbation type = {}, \n
                Arguments = {}""".format(self.perturbation_type, self.kwargs)
    
    @abstractmethod
    def perturb_method(self):
        """Mandatorily implement this method in all child classes"""


# Defines user interface   
def perturb(signal, perturbation_type = 'horizontal', **kwargs):

    """
    Function that returns an input signal after inducing a perturbation

    Parameters
    ----------
    signal : numpy.ndarray
                The input signal

    perturbation_type : str
                Type of perturbation to be induced. Defaults to 'horizontal'
                Currently supported perturbations are:
                'horizontal' = Horizontal shift
                'vertical' = Vertical shift
                'amplitude' = Amplitude variation
                'dilation' = Signal time dilation
                'gaussian' = Gaussian peak
                'peak' = Simple peak at the center of the signal
    
    kwargs: dict
                Keyword arguments to be passed depending on value of 
                'perturbation_type'

    Returns
    -------
    signal_perturbed : numpy.ndarray
                The perturbed signal

    """
    
    # Contains the perturbation_type and its corresponding mixin
    # Add a new {perturbation_type: mixin} key-value pair to 
    # register a new perturbation method
    perturb_mixin_match_dict = {
                                'horizontal': HorizontalShiftMixin,
                                'vertical': VerticalShiftMixin,
                                'dilation': SignalTimeDilationMixin,
                                'amplitude': AmplitudeVariationMixin,
                                'gaussian': GaussianPeakMixin,
                                'peak': SimplePeakMixin
                              }

    supported = list(perturb_mixin_match_dict.keys())
    
    try:
        mixin_to_use = perturb_mixin_match_dict[perturbation_type]
    except:
        raise ValueError("""
        Unsupported value '{}' for perturbation_type. 
        Currently supported perturbations are -
        {}""".format(perturbation_type, supported))

    # Throws exception if mixin_to_use is not a child of BaseMixin
    assert issubclass(mixin_to_use, BaseMixin)

    # Defines child class from base class and required mixin
    class PerturbationSimulator(PerturbationBaseClass, mixin_to_use):

        def __init__(self, signal, perturbation_type, **kwargs):
            super().__init__(signal, perturbation_type, **kwargs)
                
        def perturb_method(self):
            signal_perturbed = self.perturb_transform(signal, **self.kwargs)
            return signal_perturbed
    
    # Instatiates child class
    instance = PerturbationSimulator(signal, perturbation_type, **kwargs)
    signal_perturbed = instance.perturb_method()
    return signal_perturbed


class CyclePerturbationHelper:
    """
    Helper class that's used to apply a perturbation to the signal column in a data frame having specific structure.
    Perturbation is always returned in a new data frame. Original data frame is left untouched.
    Input data frame should have the following columns:
        - tag (string): name of the variable being sampled
        - time (numpy.datetime64): time at which the variable has been sampled
        - value (numpy.float64): sampled value
        - cycle (numpy.int64): used to group sampled measurement into sets (e.g.: group variable
            measurements collected during the execution of a process that's repeated on a regular basis)
    """
    def __init__(self, tag_col, time_col, signal_col, cycle_col, tag_list = []):
        """

        :param tags_col: name of tag column
        :param time_col: name of time column
        :param signal_col: name of signal value column
        :param cycle_col: name of cycle column
        :param tag_list: variables to which the perturbation should be applied
        """
        self.__tag_col = tag_col
        self.__time_col = time_col
        self.__signal_col = signal_col
        self.__cycle_col = cycle_col
        self.__tag_list = tag_list

    def set_tag_list(self, tag_list):
        self.__tag_list = tag_list

    def set_perturbation(self, pmixin_class):
        """

        :param pmixin_class: instance of a valid perturbation class
        :return: NA
        """
        assert (isinstance(pmixin_class, BaseMixin))
        self.__pmixin_class = pmixin_class

    def perturb_cycles(self, df):
        """
        Applies a given perturbation to the given data frame

        :param df: pandas.DataFrame
                        The input data frame
        :return df_p : pandas.DataFrame
                        The perturbed data frame
        """

        cycles_list = df[self.__cycle_col].unique()
        if len(self.__tag_list) == 0:
            tags_list_new = df[self.__tag_col].unique()
        else:
            tags_list_new = list(set(df[self.__tag_col].unique()) & set(self.__tag_list))

        if isinstance(self.__pmixin_class, SignalTimeDilationMixin):
            df_p = self.__perturb_cycles_dilation(df, cycles_list, tags_list_new)
        else:
            df_p = self.__perturb_cycles_generic(df, cycles_list, tags_list_new)
        return df_p

    def __perturb_cycles_generic(self, df, cycle_list, tag_list):
        df_test = df.copy()
        for cycle in cycle_list:
            df_cycle = df_test[df_test[self.__cycle_col] == cycle]
            for tag in tag_list:
                idxvals = df_cycle[df_cycle[self.__tag_col] == tag].index
                if len(idxvals) == 0:
                    continue
                tmp_arr = df_cycle.loc[idxvals, (self.__signal_col)].values
                tmp_arr = self.__pmixin_class.perturb_transform_(tmp_arr)
                df_test.loc[idxvals, (self.__signal_col)] = tmp_arr
        return df_test

    def __perturb_cycles_dilation(self, df, cycle_list, tag_list):
        tag_lst = []
        time_lst = []
        value_lst = []
        cycle_lst = []
        for cycle in cycle_list:
            df_cycle = df[df[self.__cycle_col] == cycle]
            for tag in tag_list:
                if len(df_cycle[df_cycle[self.__tag_col] == tag]) == 0:
                    continue
                [tag_l, time_l, value_l, cycle_l] = self.__apply_dilation(df_cycle[df_cycle[self.__tag_col] == tag])
                tag_lst.extend(tag_l)
                time_lst.extend(time_l)
                value_lst.extend(value_l)
                cycle_lst.extend(cycle_l)
        df_p = pd.DataFrame(list(zip(tag_lst, time_lst, value_lst, cycle_lst)), columns=df.columns)
        return df_p

    def __apply_dilation(self, df):
        assert (len(df.cycle.unique()) <= 1)
        assert (len(df.tag.unique()) <= 1)
        unit = np.datetime_data(df[self.__time_col].values[0])[0]
        # apply dilation to time column
        time_d = self.__pmixin_class.perturb_transform_(df[self.__time_col].values.astype('int'))
        time_d = [np.datetime64(int(t), unit) for t in time_d]
        # apply dilation to signal column
        values_d = self.__pmixin_class.perturb_transform_(df[self.__signal_col].values)
        # re-sample tag column and cycle column
        tags_d = [df.tag.unique()[0]] * len(time_d)
        cycles_d = [df.cycle.unique()[0]] * len(time_d)
        return [tags_d, time_d, values_d, cycles_d]