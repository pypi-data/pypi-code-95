"""
Sub-module of TSAnalysis

Contains classes and methods to denoise signals
"""

from tslearn.generators import random_walk_blobs, random_walks
import matplotlib.pyplot as plt
import pywt
from abc import ABCMeta, abstractmethod
import logging

logger = logging.getLogger(__name__)


# Defines denoiser mixins
class BaseMixin(metaclass = ABCMeta):
    """
    Defines pattern for child mixins
    """

    @abstractmethod
    def denoise_transform(self):
        """Mandatorily implement this method in all child mixins"""


class WaveletDenoiserMixin(BaseMixin):
    """
    Mixin class for denoising through discrete wavelet transform
    """
        
    def denoise_transform(self, signal, wavelet_type= 'sym4', level = None, 
                        threshold = 0.7, denoise_type = 'soft', axis = -1,
                        wavedec_mode = 'symmetric', threshold_mode = 'soft'):
        
        self.coeffs = pywt.wavedec(data = signal, wavelet = wavelet_type, 
                                    level = level, axis = axis, mode = wavedec_mode)
        
        for i in range(1, len(self.coeffs)):
            self.coeffs[i] = pywt.threshold(data = self.coeffs[i], 
                                            value = threshold * max(self.coeffs[i]),
                                            mode = threshold_mode)
            
        self.datarec = pywt.waverec(coeffs = self.coeffs, wavelet = wavelet_type)
        
        if signal.shape[0] != self.datarec.shape[0]:
            n = self.datarec.shape[0] - signal.shape[0]
            self.datarec = self.datarec[:-n]
            
        self.noise = signal - self.datarec
        return self.datarec, self.noise
    

# Defines base class
class DenoiserBaseClass(metaclass = ABCMeta):
    """
    Base class containing common functionality and abstract methods
    """
    
    def __init__(self, signal, denoise_type, **kwargs):
        self.signal = signal
        self.denoise_type = denoise_type
        self.kwargs = kwargs
    
    def __repr__(self):
        return """Denoise type = {}, \n
                Arguments = {}""".format(self.denoise_type, self.kwargs)
    
    @abstractmethod
    def denoise_method(self):
        """Mandatorily implement this method in all child classes"""


# Defines user interface
def denoise(signal, denoise_type = 'wavelet', return_noise = False, **kwargs):
    
    """
    Function that returns a denoised signal for an input signal

    if return_noise == True, also returns the noise component

    Parameters
    ----------
    signal : list or numpy.ndarray
            A list or numpy array of the input signal
    
    denoise_type: str
            Type of method for denoising
            Currently supported denoisers are:
            'wavelet' = Discrete wavelet transform
    
    return_noise: bool
            Flag to return the signal's noise component after denoising 
    
    kwargs: dict
            Keyword arguments to be passed depending on value of 
            'denoise_type'

    Returns
    -------
    signal_denoised: numpy.ndarray
            Denoised signal

    *if return_noise == True, also returns* 
    signal_noise: numpy.ndarray
            Noise extracted from signal during denoising
    """

    # Contains the denoise_type and its corresponding mixin
    # Add a new {denoise_type: mixin} key-value pair to 
    # register a new denoising method
    denoise_mixin_match_dict = {
                                'wavelet': WaveletDenoiserMixin
                                }

    supported = list(denoise_mixin_match_dict.keys())
    
    try:
        mixin_to_use = denoise_mixin_match_dict[denoise_type]
    except:
        raise ValueError("""
        Unsupported value '{}' for denoise_type. 
        Currently supported denoisers are - 
        {}""".format(denoise_type, supported))

    # Throws exception if mixin_to_use is not a child of BaseMixin
    assert issubclass(mixin_to_use, BaseMixin)

    # Defines child class from base class and required mixin
    class Denoiser(DenoiserBaseClass, mixin_to_use):
        
        def __init__(self, signal, denoise_type, **kwargs):
            super().__init__(signal, denoise_type, **kwargs)
        
        def denoise_method(self):
            signal_denoised, signal_noise = self.denoise_transform(signal, **self.kwargs)
            return signal_denoised, signal_noise

    # Instantiates child class
    instance = Denoiser(signal, denoise_type, **kwargs)
    signal_denoised, signal_noise = instance.denoise_method()

    if return_noise == True:
        logger.info("Output returned as (np.array(denoise_signal), np.array(noise))")
        return signal_denoised, signal_noise
    else:
        return signal_denoised
        