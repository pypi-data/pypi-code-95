"""
=======
Raw EEG
=======
"""

from bci_framework.extensions.visualizations import EEGStream, interact
from bci_framework.extensions.data_analysis import loop_consumer, fake_loop_consumer
from bci_framework.extensions import properties as prop
import numpy as np
from scipy.fftpack import fft, fftfreq, fftshift
from scipy.signal import welch

from gcpds.filters import frequency as flt
import logging


notch_filters = ('None', '50 Hz', '60 Hz')

bandpass_filters = ('None', 'delta', 'theta', 'alpha', 'beta',
                    '5-45 Hz', '3-30 Hz', '4-40 Hz', '2-45 Hz', '1-50 Hz',
                    '7-13 Hz', '15-50 Hz', '1-100 Hz', '5-50 Hz',)


########################################################################
class RawEEG(EEGStream):

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        BUFFER = 2

        self.mode = 'Fourier'

        self.axis = self.add_subplot(111)
        self.create_buffer(BUFFER, aux_shape=3, fill=0)

        window = BUFFER * prop.SAMPLE_RATE
        self.W = fftshift(fftfreq(window, 1 / prop.SAMPLE_RATE))

        a = np.empty(window)
        a.fill(0)
        self.lines = [self.axis.plot(self.W, a.copy(), '-',)[0]
                      for i in range(len(prop.CHANNELS))]

        self.axis.set_xlim(0, 100)
        self.axis.set_ylim(0, 1)
        self.axis.set_xlabel('Frequency [Hz]')
        self.axis.set_ylabel('Amplitude')

        self.stream()

    # ----------------------------------------------------------------------
    def autoscale(self, data):
        """"""
        data = data - data.mean()
        data = data / (data.max() - data.min())
        return data

    # ----------------------------------------------------------------------
    @loop_consumer('eeg')
    def stream(self, frame):

        if frame % 3:
            return

        eeg = self.buffer_eeg
        self.axis.collections.clear()

        if self.mode == 'Fourier':
            EEG = fftshift(np.abs(fft(eeg)))
            self.W = fftshift(fftfreq(EEG.shape[1], 1 / prop.SAMPLE_RATE))

        elif self.mode == 'Welch':
            EEG, self.W = welch(eeg, prop.SAMPLE_RATE, window='flattop',
                                nperseg=100, scaling='spectrum', axis=-1)

        EEG = EEG / EEG.max()
        for i, line in enumerate(self.lines):
            if self.mode == 'Fourier':
                line.set_ydata(EEG[i])
                self.axis.fill_between(
                    self.W, EEG[i], 0, facecolor=f'C{i}', alpha=0.1)

            elif self.mode == 'Welch':
                line.set_ydata(EEG[i])

        self.axis.set_xlim(0, 100)

        self.feed()

    # ----------------------------------------------------------------------

    @interact('BandPass', bandpass_filters, 'None')
    def interact_bandpass(self, bandpass):
        """"""
        if bandpass == 'None':
            self.remove_transformers(['bandpass'])
        elif bandpass in ['delta', 'theta', 'alpha', 'beta']:
            bandpass = getattr(flt, bandpass)
            self.add_transformers({'bandpass': bandpass})
        else:
            bandpass = bandpass.replace(' Hz', '').replace('-', '')
            bandpass = getattr(flt, f'band{bandpass}')
            self.add_transformers({'bandpass': bandpass})

    # ----------------------------------------------------------------------
    @interact('Notch', notch_filters, 'None')
    def interact_notch(self, notch):
        """"""
        if notch == 'None':
            self.remove_transformers(['notch'])
        else:
            notch = notch.replace(' Hz', '')
            notch = getattr(flt, f'notch{notch}')
            self.add_transformers({'notch': notch})

    # ----------------------------------------------------------------------
    @interact('Mode', ('Fourier', 'Welch'), 'Fourier')
    def interact_mode(self, mode):
        """"""
        self.mode = mode


if __name__ == '__main__':
    RawEEG()
