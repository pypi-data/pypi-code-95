import mne
import numpy as np

'''
https://realpython.com/pypi-publish-python-package/#publishing-to-pypi
https://towardsdatascience.com/how-to-publish-a-python-package-to-pypi-7be9dd5d6dcd
'''
class sim_data:
    def __init__ (self):
        b = 1

    def gen_epochs (self, nchannels=None, labels=None, sfreq=None,
                    ntimes=None, n_epcohs=None):
        # Generate data

        if (nchannels is None) & (labels is None):
            labels_ch = ['FP1', 'FP2', 'F3', 'F4', 'F7', 'F8', 'C3', 'C4',
                         'T3', 'T4', 'O1', 'O2']
            N_channels = len ( labels_ch )

        elif (labels is None) & (nchannels is not None):

            if not isinstance ( nchannels, int ):
                raise ('Please provide type int')

            N_channels = nchannels
            nrange_ch = range ( 0, nchannels )
            labels_ch = [f'EEG_{idx}' for idx in nrange_ch]


        elif (nchannels is None) & (labels is not None):
            if not isinstance ( labels, list ):
                raise ('Please provide type list: ["EEG_1","EEG_2"]')

            labels_ch = labels
            N_channels = len ( labels )

        N_epochs = 5 if n_epcohs is None else n_epcohs
        N_times = 1000 if ntimes is None else ntimes
        # Set sampling freq
        Sfreqs = 250 if sfreq is None else sfreq  # A reasonable random choice

        np.random.seed ( 42 )

        data = np.random.rand ( N_epochs, N_channels, N_times )

        # 10Hz sinus waves with random phase differences in each channel and epoch
        # Generate 10Hz sinus waves to show difference between connectivity
        # over time and over trials. Here we expect con over time = 1
        for i in range ( N_epochs ):
            for c in range ( N_channels ):
                wave_freq = 10
                epoch_len = N_times / Sfreqs
                # Introduce random phase for each channel
                phase = np.random.rand ( 1 ) * 10
                # Generate sinus wave
                x = np.linspace ( -wave_freq * epoch_len * np.pi + phase,
                                  wave_freq * epoch_len * np.pi + phase, N_times )
                data [i, c] = np.squeeze ( np.sin ( x ) )

        info = mne.create_info ( ch_names=labels_ch,
                                 ch_types=['eeg'] * len ( labels_ch ),
                                 sfreq=Sfreqs )

        epochs = mne.EpochsArray ( data, info )
        return epochs


# sg = simeeg ()
# ep = sg.gen_epochs ( labels=['A','B','C'] )
