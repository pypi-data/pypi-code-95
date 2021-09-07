import h5py
import numpy as np
import time

from aermanager.aerparser import load_events_from_file
from aermanager.dataset_generator import dataset_content_generator


def timeit(func):
    def wrapper():
        t_start = time.time()
        data = func()
        print(len(data), type(data[-1]))
        t_stop = time.time()
        t_run = t_stop-t_start
        print(f"Time to run {func} : {t_run}")
        return data, t_run
    return wrapper


def save_events(time_window=True):
    shape, xytp = load_events_from_file("cars_oh_highway.aedat4", "aedat4")

    if time_window:
        indices, sliced_xytp, frames = dataset_content_generator("cars_oh_highway.aedat4",
                                                                 time_window=50000)
    else:
        indices, sliced_xytp, frames = dataset_content_generator("cars_oh_highway.aedat4",
                                                                 spike_count=1000)
    compression = None
    indices = np.concatenate([[0], indices])

    with h5py.File("h5file_test_data_non_sliced.h5", 'w') as F:
        F.create_dataset('frames', data=frames, compression=compression)
        F.create_dataset('frames_start_indices', data=indices)
        F.create_dataset('spikes/t', data=xytp['t'], compression=compression)
        F.create_dataset('spikes/x', data=xytp['x'], compression=compression)
        F.create_dataset('spikes/y', data=xytp['y'], compression=compression)
        F.create_dataset('spikes/p', data=xytp['p'], compression=compression)

    for i, slice in enumerate(sliced_xytp):
        with h5py.File(f"dataset/{i}.h5", 'w') as F:
            F.create_dataset('frame', data=frames[i], compression=compression)
            F.create_dataset('frames_start_index', data=indices[i])
            F.create_dataset(f'spikes/t', data=slice['t'], compression=compression)
            F.create_dataset(f'spikes/x', data=slice['x'], compression=compression)
            F.create_dataset(f'spikes/y', data=slice['y'], compression=compression)
            F.create_dataset(f'spikes/p', data=slice['p'], compression=compression)


def test_multifile_vs_single():
    save_events()
    n_runs = 1000

    @timeit
    def load_hdf5_non_sliced():
        for i in np.random.randint(0, 100, n_runs):
            with h5py.File("h5file_test_data_non_sliced.h5", "r") as hf:
                indices = hf["frames_start_indices"][()]
                index_start = indices[i]
                index_end = indices[i+1]
                t = hf["spikes"]["t"][index_start:index_end][()]
                x = hf["spikes"]["x"][index_start:index_end][()]
                y = hf["spikes"]["y"][index_start:index_end][()]
                p = hf["spikes"]["p"][index_start:index_end][()]
                frame = hf["frames"][i][()]
                assert (frame.sum() == len(t))
        return x, y, t, p, frame


    @timeit
    def load_hdf5_multi_file():
        for i in np.random.randint(0, 100, n_runs):
            with h5py.File(f"dataset/{i}.h5", "r") as hf:
                start_index = hf["frames_start_index"]
                t = hf["spikes"]["t"][()]
                x = hf["spikes"]["x"][()]
                y = hf["spikes"]["y"][()]
                p = hf["spikes"]["p"][()]
                frame = hf["frame"][()]
                assert (frame.sum() == len(t))
        return x, y, t, p, frame

    load_hdf5_non_sliced()
    load_hdf5_multi_file()
