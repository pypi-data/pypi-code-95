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


def test_speed():
    save_data()

    @timeit
    def load_numpy():
        data = np.load("npzfile_test_data.npz")["data"]
        return data

    @timeit
    def load_hdf5():
        with h5py.File("h5file_test_data.h5", "r") as hf:
            data = hf["data"][:]
        return data

    _, runtime_numpy = load_numpy()
    _, runtime_hdf5 = load_hdf5()

    assert(runtime_hdf5 < runtime_numpy)


def save_data():
    data = np.random.rand(100, 100, 100)
    with h5py.File("h5file_test_data.h5", "w") as hf:
        hf.create_dataset("data", data=data)

    np.savez("npzfile_test_data", data=data)


def save_events(time_window=False):
    shape, xytp = load_events_from_file("cars_oh_highway.aedat4", None)

    if time_window:
        indices, sliced_xytp, frames = dataset_content_generator("cars_oh_highway.aedat4",
                                                                 time_window=50000)
    else:
        indices, sliced_xytp, frames = dataset_content_generator("cars_oh_highway.aedat4",
                                                                 spike_count=1000)
    compression = "lzf"
    with h5py.File("h5file_test_data_sliced.h5", 'w') as F:
        F.create_dataset('frames', data=frames, compression=compression)
        F.create_dataset('frames_start_indices', data=indices)
        for i, slice in enumerate(sliced_xytp):
            F.create_dataset(f'spikes/{i}/t', data=slice['t'], compression=compression)
            F.create_dataset(f'spikes/{i}/x', data=slice['x'], compression=compression)
            F.create_dataset(f'spikes/{i}/y', data=slice['y'], compression=compression)
            F.create_dataset(f'spikes/{i}/p', data=slice['p'], compression=compression)

    with h5py.File("h5file_test_data_non_sliced.h5", 'w') as F:
        F.create_dataset('frames', data=frames, compression=compression)
        F.create_dataset('frames_start_indices', data=indices)
        F.create_dataset('spikes/t', data=xytp['t'], compression=compression)
        F.create_dataset('spikes/x', data=xytp['x'], compression=compression)
        F.create_dataset('spikes/y', data=xytp['y'], compression=compression)
        F.create_dataset('spikes/p', data=xytp['p'], compression=compression)

    np.savez("npzfile_test_data_non_sliced.npz", frames=frames, frames_start_indices=indices,
                        t=xytp["t"], x=xytp["x"], y=xytp["y"], p=xytp["p"])


def test_hdf5_slicing_speeds_spike_count():
    save_events(time_window=False)
    n_runs = 1000

    @timeit
    def load_hdf5_sliced():
        for i in np.random.randint(0, 100, n_runs):
            with h5py.File("h5file_test_data_sliced.h5", "r") as hf:
                # indices = hf["frames_start_indices"][()]
                t = hf["spikes"][str(i)]["t"][()]
                x = hf["spikes"][str(i)]["x"][()]
                y = hf["spikes"][str(i)]["y"][()]
                p = hf["spikes"][str(i)]["p"][()]
                frame = hf["frames"][i][()]
                assert(frame.sum() == len(t))
        return x, y, t, p, frame

    @timeit
    def load_hdf5_non_sliced():
        for i in np.random.randint(0, 100, n_runs):
            with h5py.File("h5file_test_data_non_sliced.h5", "r") as hf:
                indices = hf["frames_start_indices"][()]
                t = hf["spikes"]["t"][indices[i]:indices[i+1]][()]
                x = hf["spikes"]["x"][indices[i]:indices[i+1]][()]
                y = hf["spikes"]["y"][indices[i]:indices[i+1]][()]
                p = hf["spikes"]["p"][indices[i]:indices[i+1]][()]
                frame = hf["frames"][i][()]
                assert(frame.sum() == len(t))
        return x, y, t, p, frame

    _, runtime_sliced = load_hdf5_sliced()
    _, runtime_non_sliced = load_hdf5_non_sliced()


def test_hdf5_slicing_speeds_time_window():
    save_events(time_window=True)
    n_runs = 1000

    @timeit
    def load_hdf5_sliced():
        for i in np.random.randint(0, 100, n_runs):
            with h5py.File("h5file_test_data_sliced.h5", "r") as hf:
                # indices = hf["frames_start_indices"][()]
                t = hf["spikes"][str(i)]["t"][()]
                x = hf["spikes"][str(i)]["x"][()]
                y = hf["spikes"][str(i)]["y"][()]
                p = hf["spikes"][str(i)]["p"][()]
                frame = hf["frames"][i][()]
                assert(frame.sum() == len(t))
        return x, y, t, p, frame

    @timeit
    def load_hdf5_non_sliced():
        for i in np.random.randint(0, 100, n_runs):
            with h5py.File("h5file_test_data_non_sliced.h5", "r") as hf:
                indices = np.concatenate([[0], hf["frames_start_indices"][()]])
                t = hf["spikes"]["t"][indices[i]:indices[i+1]][()]
                x = hf["spikes"]["x"][indices[i]:indices[i+1]][()]
                y = hf["spikes"]["y"][indices[i]:indices[i+1]][()]
                p = hf["spikes"]["p"][indices[i]:indices[i+1]][()]
                frame = hf["frames"][i][()]
                assert(frame.sum() == len(t))
        return x, y, t, p, frame

    _, runtime_sliced = load_hdf5_sliced()
    _, runtime_non_sliced = load_hdf5_non_sliced()


def test_npz_hdf5_events_compressed():
    save_events(time_window=True)

    n_runs = 100

    @timeit
    def load_hdf5_non_sliced():
        for i in np.random.randint(0, 100, n_runs):
            with h5py.File("h5file_test_data_non_sliced.h5", "r") as hf:
                indices = np.concatenate([[0], hf["frames_start_indices"][:]])
                t = hf["spikes"]["t"][indices[i]:indices[i + 1]][:]
                x = hf["spikes"]["x"][indices[i]:indices[i + 1]][:]
                y = hf["spikes"]["y"][indices[i]:indices[i + 1]][:]
                p = hf["spikes"]["p"][indices[i]:indices[i + 1]][:]
                frame = hf["frames"][i][:]
                assert (frame.sum() == len(t))
        return x, y, t, p, frame

    @timeit
    def load_npz_non_sliced():
        for i in np.random.randint(0, 100, n_runs):
            with np.load("npzfile_test_data_non_sliced.npz", mmap_mode="r") as hf:
                indices = np.concatenate([[0], hf["frames_start_indices"][:]])
                t = hf["t"][indices[i]:indices[i + 1]][:]
                x = hf["x"][indices[i]:indices[i + 1]][:]
                y = hf["y"][indices[i]:indices[i + 1]][:]
                p = hf["p"][indices[i]:indices[i + 1]][:]
                frame = hf["frames"][i][:]
                assert (frame.sum() == len(t))
        return x, y, t, p, frame

    load_hdf5_non_sliced()
    load_npz_non_sliced()


