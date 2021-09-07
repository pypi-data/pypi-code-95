import warnings
import h5py
from tqdm import tqdm
from pathlib import Path
import numpy as np
from typing import Optional, Tuple, Callable, Union
from aermanager.parsers import parse_aedat4
from aermanager.aerparser import load_events_from_file
from aermanager.preprocess import crop_events, filter_hot_pixels, slice_by_time, slice_by_count, accumulate_frames
from aermanager.annotate_aedat import annotate_events
import hashlib


def _get_md5(file):
    with open(file, "rb") as f:
        return hashlib.md5(f.read(4096)).hexdigest()


def dataset_content_generator(file_name: str,
                              crop_size: Optional[Tuple[Tuple]] = None,
                              hot_pixel_frequency: Optional[float] = None,
                              time_window: Optional[int] = None,
                              spike_count: Optional[int] = None,
                              parser: Union[Callable, str] = parse_aedat4,
                              tags_file_path: Optional[str] = None,
                              rois_file_path: Optional[str] = None, ):
    """
    Main function for generating a folder of separate HDF5 files containing frames
    and the corresponding spiketrains, starting from an individual file.

    Args:
        file_name (str): Input events file to be converted
        crop_size (Tuple(Tuple)): A tuple of the borders to crop ((left, right), (top, bottom))
        hot_pixel_frequency (float): Threshold frequency for hot pixel in Hz
        time_window (int): Length of accumulated frames, in microseconds (set either this or spike_count)
        spike_count (int): Length of accumulated frames, in spike count (set either this or time_window)
        parser (Callable, str): A callable that returns (shape, xytp), defaults to parse_aedat4

    Returns:
        sliced_xytp (list): A list of structured arrays containing spike events. Each array corresponds to a frame.
        frames (np.ndarray): A 4-d array of frames, (time, channels, y, x).
    """
    assert ((time_window is None) ^ (spike_count is None))

    shape, xytp = load_events_from_file(file_name, parser)

    if crop_size:
        xytp, shape = crop_events(xytp, input_shape=shape, crop_size=crop_size)

    if hot_pixel_frequency:
        xytp = filter_hot_pixels(xytp,
                                 shape=shape,
                                 hot_pixel_frequency=hot_pixel_frequency)

    if tags_file_path or rois_file_path:
        xytp = annotate_events(xytp, rois_file_path, tags_file_path)

    if time_window:
        sliced_xytp = slice_by_time(xytp, time_window, overlap=0)
    else:
        sliced_xytp = slice_by_count(xytp, spike_count, overlap=0)

    bins_yx = (range(shape[0] + 1), range(shape[1] + 1))

    frames = accumulate_frames(sliced_xytp, *bins_yx)

    return sliced_xytp, frames, bins_yx


def save_to_hdf5(xytp, frame, label, bins, file_name, compression=None):
    """
    Function that takes care of the actual opening and saving of a single HDF5 file.
    It exists in order to make sure the HDF5 format is standardized.

    Args:
        xytp (list): A structured array containing spike events corresponding to the frame.
        frames (np.ndarray): A 3-d array, (channels, y, x).
        labels (list): The label corresponding to this frame.
        bins (list, list): bins_y and bins_x based on which the frame was generated.
        destination_path (path or str): The name of the file to save to.
        compression (str or None): Compression algorithm to pass to HDF5 (None, 'lzf', 'gzip')
    """
    with h5py.File(file_name, 'w') as F:
        F.create_dataset('frame', data=frame, compression=compression)
        F.create_dataset('label', data=label)
        F.create_dataset('spikes/t', data=xytp['t'], compression=compression)
        F.create_dataset('spikes/x', data=xytp['x'], compression=compression)
        F.create_dataset('spikes/y', data=xytp['y'], compression=compression)
        F.create_dataset('spikes/p', data=xytp['p'], compression=compression)
        F.create_dataset('bins/x', data=bins[1])
        F.create_dataset('bins/y', data=bins[0])


def save_to_dataset(sliced_xytp, frames, labels, bins,
                    destination_path, compression: Optional[str] = None):
    """
    Saves a folder of HDF5 files from accumulated frames and spiketrains.

    Args:
        sliced_xytp (list): A list of structured arrays containing spike events. Each array corresponds to a frame.
        frames (np.ndarray): A 4-d array of frames, (time, channels, y, x).
        labels (list): A list of labels, one per frame
        bins (list, list): bins_y and bins_x based on which the frames were generated.
        destination_path (path or str): Folder where the output is saved
        compression (str or None): Compression algorithm to pass to HDF5 (None, 'lzf', 'gzip')
    """

    # TODO: Could write metadata or create separate text file for them.
    # warnings.warn("Meta-data are not saved")

    path = Path(destination_path)
    path.mkdir(parents=True, exist_ok=True)

    for i, slc in enumerate(sliced_xytp):
        file_name = path / f"{i}.h5"
        save_to_hdf5(
            xytp=slc,
            frame=frames[i],
            label=labels[i],
            bins=bins,
            file_name=file_name,
            compression=compression
        )


# Single File
def gen_dataset_from_list(
        event_files,
        labels,
        destination_path,
        compression: Optional[str] = None,
        crop_size: Optional[Tuple[Tuple]] = None,
        hot_pixel_frequency: Optional[float] = None,
        time_window: Optional[int] = None,
        spike_count: Optional[int] = None,
        parser: Union[Callable, str] = parse_aedat4, ):
    """
    Main function for generating a folder of separate HDF5 files containing frames
    and the corresponding spiketrains, starting from a list of files and labels.

    Args:
        event_files (list): A list of file paths with events data.
        labels (list): A list of labels, one per input file.
        destination_path (path or str): Folder where the output is saved
        compression (str or None): Compression algorithm to pass to HDF5 (None, 'lzf', 'gzip')
        crop_size (Tuple(Tuple)): A tuple of the borders to crop ((left, right), (top, bottom))
        hot_pixel_frequency (float): Threshold frequency for hot pixel in Hz
        time_window (int): Length of accumulated frames, in microseconds (set either this or spike_count)
        spike_count (int): Length of accumulated frames, in spike count (set either this or time_window)
        parser (Callable, str): A callable that returns (shape, xytp), defaults to parse_aedat4
    """
    destination_path = Path(destination_path)
    destination_path.mkdir(parents=True, exist_ok=True)

    for fname, label in tqdm(zip(event_files, labels)):
        hash_code = _get_md5(fname)

        sliced_xytp, frames, bins_yx = dataset_content_generator(
            fname,
            crop_size=crop_size,
            hot_pixel_frequency=hot_pixel_frequency,
            time_window=time_window,
            spike_count=spike_count,
            parser=parser,
        )

        name = (Path(fname).with_suffix("").name + "_" + hash_code[:5])
        folder_path = destination_path / name

        if folder_path.exists():
            warnings.warn(f"Folder {folder_path} already exists", stacklevel=2)

        save_to_dataset(sliced_xytp, frames, [label] * len(sliced_xytp),
                        bins=bins_yx,
                        destination_path=folder_path, compression=compression)


# CSV dataloader
def gen_dataset_from_csv(
        csv_file,
        destination_path,
        delimiter=",",
        source_folder=None,
        compression: Optional[str] = None,
        crop_size: Optional[Tuple[Tuple]] = None,
        hot_pixel_frequency: Optional[float] = None,
        time_window: Optional[int] = None,
        spike_count: Optional[int] = None,
        parser: Union[Callable, str] = parse_aedat4, ):
    """
    Function for reading a CSV file with file paths and labels, and generate
    a dataset from it. The file should have two columns, separated by `delimiter`:
    the first contains file URLs, the second is interpreted as labels.

    Args:
        csv_file (path or str): The address of the input CSV file
        destination_path (path or str): Folder where the output is saved
        delimiter (str): The delimiter for the columns in the CSV file, default ','
        source_folder (path or str): Root path from which the file_names are provided.
        compression (str or None): Compression algorithm to pass to HDF5 (None, 'lzf', 'gzip')
        crop_size (Tuple(Tuple)): A tuple of the borders to crop ((left, right), (top, bottom))
        hot_pixel_frequency (float): Threshold frequency for hot pixel in Hz
        time_window (int): Length of accumulated frames, in microseconds (set either this or spike_count)
        spike_count (int): Length of accumulated frames, in spike count (set either this or time_window)
        parser (Callable, str): A callable that returns (shape, xytp), defaults to parse_aedat4
    """
    files, labels = np.loadtxt(csv_file, delimiter=delimiter,
                               dtype=(str, str), unpack=True)
    if source_folder is not None:
        source_folder = Path(source_folder)
        files = [source_folder / f for f in files]
    labels = [lb.strip() for lb in labels]

    gen_dataset_from_list(
        event_files=files,
        labels=labels,
        destination_path=destination_path,
        compression=compression,
        crop_size=crop_size,
        hot_pixel_frequency=hot_pixel_frequency,
        time_window=time_window,
        spike_count=spike_count,
        parser=parser
    )


def _get_lists_from_subfolders(source_path, pattern="*.aedat*"):
    source_path = Path(source_path)
    subflist = [f for f in source_path.iterdir() if f.is_dir()]
    subflist = sorted(subflist)

    files = []
    labels = []

    for folder in subflist:
        files_here = list(folder.glob(pattern))
        files.extend(files_here)
        labels.extend([folder.name] * len(files_here))

    return files, labels


# Folder based dataloader
def gen_dataset_from_folders(
        source_path,
        destination_path,
        pattern="*.aedat*",
        compression: Optional[str] = None,
        crop_size: Optional[Tuple[Tuple]] = None,
        hot_pixel_frequency: Optional[float] = None,
        time_window: Optional[int] = None,
        spike_count: Optional[int] = None,
        parser: Union[Callable, str] = parse_aedat4,
):
    """
    Function for reading event files from a structured folder, and generate
    a dataset from it. The folder's subfolders are interpreted as labels, and
    each file in them is read.

    Args:
        source_path (path or str): The address of the source folder
        destination_path (path or str): Folder where the output is saved
        pattern (str): File name patterns to use for creating the dataset. Defaults to '*.aedat*'
        compression (str or None): Compression algorithm to pass to HDF5 (None, 'lzf', 'gzip')
        crop_size (Tuple(Tuple)): A tuple of the borders to crop ((left, right), (top, bottom))
        hot_pixel_frequency (float): Threshold frequency for hot pixel in Hz
        time_window (int): Length of accumulated frames, in microseconds (set either this or spike_count)
        spike_count (int): Length of accumulated frames, in spike count (set either this or time_window)
        parser (Callable, str): A callable that returns (shape, xytp), defaults to parse_aedat4
    """
    files, labels = _get_lists_from_subfolders(source_path, pattern=pattern)

    if len(files) == 0:
        raise FileNotFoundError(f"No files with extension `{pattern}` found in {source_path}.")

    gen_dataset_from_list(
        event_files=files,
        labels=labels,
        destination_path=destination_path,
        compression=compression,
        crop_size=crop_size,
        hot_pixel_frequency=hot_pixel_frequency,
        time_window=time_window,
        spike_count=spike_count,
        parser=parser,
    )
