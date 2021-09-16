from openbci_stream.utils import HDF5Reader


# filename = 'record-09_15_21-16_00_11.h5'
filename = 'record-09_15_21-17_41_16.h5'
with HDF5Reader(filename) as reader:

    eeg = reader.eeg.copy()
    t = reader.timestamp.copy()
    m = reader.markers.copy()


m
