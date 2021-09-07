import numpy as np
from typing import Tuple, List
from .parsers import make_structured_array


def crop_events(xytp: np.ndarray, input_shape: Tuple, crop_size: Tuple):
    """
    Crop events

    Args:
        xytp (np.ndarray):  Structured array of events
        input_shape (Tuple): A tuple (height, width)
        crop_size (Tuple(Tuple)): A tuple of the borders to crop ((left, right), (top, bottom))

    Returns:
        cropped_xytp (np.ndarray): Structured array of events.
        The pixel addresses are shifted to origin after cropping
    """
    (left, right), (top, bottom) = crop_size
    x_lo, y_lo = 0, 0
    y_hi, x_hi, = input_shape
    x_hi -= 1
    y_hi -= 1

    x, y = xytp["x"], xytp["y"]

    keepidx = (
            (x >= x_lo + left)
            & (x <= x_hi - right)
            & (y >= y_lo + top)
            & (y <= y_hi - bottom)
    )

    xytp_cropped = xytp[keepidx]
    xytp_cropped["x"] -= left
    xytp_cropped["y"] -= top

    new_shape = (input_shape[0] - top - bottom), (input_shape[1] - left - right)

    return xytp_cropped, new_shape


def resize_events(xytp, shape):
    """
    Centerize a xytp of events to a larger frame-shape.

    Args:
        xytp: Slice of events.
        shape (Tuple): Shape of the output frame of xytp (height, width)
    Returns:
        xytp: Resized xytp of events.
    """
    # TODO: Ensure that the input is trimmed in case it is larger than the shape specified
    max_x, max_y = max(xytp['x']), max(xytp['y'])
    min_x, min_y = min(xytp['x']), min(xytp['y'])
    x_len = max_x - min_x
    y_len = max_y - min_y
    xytp_x = xytp['x'] - min(xytp['x'])
    xytp_y = xytp['y'] - min(xytp['y'])

    xytp_x += int(shape[1] / 2) - int(x_len / 2)
    xytp_y += int(shape[0] / 2) - int(y_len / 2)
    return make_structured_array(xytp_x, xytp_y, xytp['t'], xytp['p'])



def crop_frame(frame: np.ndarray, crop_size: Tuple):
    """
    Crop events

    Args:
        frame(np.ndarray): numpy array of a frame of dimensions (channels, height, width)
        crop_size (Tuple(Tuple)): A tuple of the borders to crop ((left, right), (top, bottom))

    Returns:
        cropped_frame (np.ndarray): numpy array of a frame of dimensions (channels, height, width)
    """
    (left, right), (top, bottom) = crop_size
    return frame[:, top: -bottom, left:-right]


def slice_by_time(xytp: np.ndarray, time_window:int, overlap:int = 0, include_incomplete=False):
    """
    Return xytp split according to fixed timewindow and overlap size
    <        <overlap>        >
    |   window1      |
             |   window2      |

    Args:
        xytp: np.ndarray
            Structured array of events
        time_window: int
            Length of time for each xytp (ms)
        overlap: int
            Length of time of overlapping (ms)
        include_incomplete: bool
            include incomplete slices ie potentially the last xytp

    Returns:
        slices List[np.ndarray]: Data slices

    """
    t = xytp["t"]
    stride = time_window - overlap
    assert stride > 0

    if include_incomplete:
        n_slices = int(np.ceil(((t[-1] - t[0]) - time_window) / stride) + 1)
    else:
        n_slices = int(np.floor(((t[-1] - t[0]) - time_window) / stride) + 1)
    n_slices = max(n_slices, 1) # for strides larger than recording time

    tw_start = np.arange(n_slices)*stride + t[0]
    tw_end = tw_start + time_window
    indices_start = np.searchsorted(t, tw_start)
    indices_end = np.searchsorted(t, tw_end)
    sliced_xytp = [xytp[indices_start[i]:indices_end[i]] for i in range(n_slices)]
    return sliced_xytp


def slice_by_count(xytp: np.ndarray, spike_count: int, overlap: int = 0, include_incomplete=False):
    """
    Return xytp sliced nto equal number of events specified by spike_count

    Args:
        xytp (np.ndarray):  Structured array of events
        spike_count (int):  Number of events per xytp
        overlap: int
            No. of spikes overlapping in the following xytp(ms)
        include_incomplete: bool
            include incomplete slices ie potentially the last xytp
    Returns:
        slices (List[np.ndarray]): Data slices
    """
    n_spk = len(xytp)
    spike_count = min(spike_count, n_spk)
    stride = spike_count - overlap
    assert stride > 0

    if include_incomplete:
        n_slices = int(np.ceil((n_spk - spike_count) / stride) + 1)
    else:
        n_slices = int(np.floor((n_spk - spike_count) / stride) + 1)

    indices_start = np.arange(n_slices)*stride
    indices_end = indices_start + spike_count
    sliced_xytp = [xytp[indices_start[i]:indices_end[i]] for i in range(n_slices)]
    return sliced_xytp


def slice_by_indices(xytp: np.ndarray, start_indices, end_indices):
    """
    Return xytp sliced into equal number of events specified by spike_count

    Args:
    -----
        xytp (np.ndarray):  Structured array of events
        start_indices: (List[Int]): List of start indices
        end_indices: (List[Int]): List of end indices (exclusive)
    Returns:
    --------
    slices (np.ndarray): Data slices
    """
    t = xytp["t"]
    indices_start = np.searchsorted(t, start_indices)
    indices_end = np.searchsorted(t, end_indices)
    sliced_xytp = [xytp[indices_start[i]:indices_end[i]] for i in range(len(indices_start))]
    return sliced_xytp


def accumulate_frames(list_xytp: List[np.ndarray], bins_y, bins_x) -> np.ndarray:
    """
    Convert xytp event lists to frames

    Args:
        list_xytp (List[np.ndarray]): A *list* of xytp, where each element in the list is a structured array of events
        bins_y (ListLike):  Bins to use for creating the frame
        bins_x (ListLike):  Bins to use for creating the frame

        Note: bins_y and bins_x are typically range(0, height_of_sensor) and range(0, width_of_sensor)
    Returns:
        raster: (np.ndaray): Numpy array with dimensions [N, polarity, height, width], where N is the length of list_xytp
    """
    frames = np.empty((len(list_xytp), 2, len(bins_y) - 1, len(bins_x) - 1), dtype=np.uint16)
    for i, slice_item in enumerate(list_xytp):
        frames[i] = np.histogramdd((slice_item["p"], slice_item["y"], slice_item["x"]),
                                   bins=((-1, 0.5, 2), bins_y, bins_x))[0]
    return frames


def identify_hot_pixels(xytp, shape: Tuple, hot_pixel_frequency: float):
    """
    Identify hot pixels with the given criterion

    Args:
        xytp (np.ndarray):  Structured array of events
        shape (Tuple): A tuple (height, width)
        hot_pixel_frequency (float): Threshold frequency for hot pixel in Hz

    Returns:
        hotpixels  : List of (x, y)

    """
    x, y = xytp["x"], xytp["y"]
    tottime = xytp["t"][-1] - xytp["t"][0]
    # xmin, ymin = 0, 0
    bins_x = np.arange(shape[1] + 1)
    bins_y = np.arange(shape[0] + 1)

    hist = np.histogram2d(x, y, bins=(bins_x, bins_y))[0]
    max_occur = hot_pixel_frequency * tottime * 1e-6
    hot_pixels = np.asarray((hist > max_occur).nonzero()).T
    return hot_pixels


def filter_hot_pixels(xytp, shape: Tuple, hot_pixel_frequency: float):
    """
    Filter hot pixels with the given criterion

    Args:
        xytp (np.ndarray):  Structured array of events
        shape (Tuple): A tuple (height, width)
        hot_pixel_frequency (float): Threshold frequency for hot pixel in Hz

    Returns:
        xytp_filtered (np.ndarray)  : Structured array of events

    """
    x, y = xytp["x"], xytp["y"]
    hot_pixels = identify_hot_pixels(xytp, shape, hot_pixel_frequency)

    mask = np.zeros(len(x), dtype=bool)
    for hp in hot_pixels:  # sigh (but 4x faster than np.unique)
        is_hot = np.logical_and(x == hp[0], y == hp[1])
        mask = np.logical_or(mask, is_hot)

    print(f"Found {len(hot_pixels)} hot pixels")
    print(f"Removed {mask.sum()} spikes from hot pixels")

    return xytp[~mask]


def create_raster_from_xytp(xytp: np.ndarray, dt: int, bins_y, bins_x):
    """
    Convert xytp events to a raster

    Args:
        xytp (np.ndarray):  Structured array of events
        dt (int):           Time window per xytp in the raster
        bins_y (ListLike):  Bins to use for creating the frame
        bins_x (ListLike):  Bins to use for creating the frame

        Note: bins_y and bins_x are typically range(0, height_of_sensor) and range(0, width_of_sensor)
    Returns:
        raster: (np.ndaray): Numpy array with dimensions [time, polarity, height, width]
    """
    sliced_xytp = slice_by_time(xytp, time_window=dt, include_incomplete=True)
    return accumulate_frames(sliced_xytp, bins_y, bins_x).astype(np.float32)


def create_hybrid_uniform_raster(list_xytp: List[np.ndarray], shape: tuple):
    """
    Convert xytp events to a raster by making a hybrid raster that maintains uniform spiking activity per step

    Args:

        xytp (List[np.ndarray]):  Structured array of events
        shape (tuple(int, int)):  The x, y dimension

    Returns:
        raster_list: (List[np.ndarray]): List of processed rasters with shape of [step, 2, y, x]
    """
    raster_list = []
    y, x = shape
    for xytp in list_xytp:

        raster = np.zeros((1, 2, y, x))
        raster_counter = 0
        for ev in xytp:

            if raster[raster_counter, int(ev["p"]), ev["y"], ev["x"]] == 0:
                raster[raster_counter, int(ev["p"]), ev["y"], ev["x"]] += 1
            else:
                raster_counter += 1
                next_raster = np.zeros((1, 2, y, x))
                raster = np.concatenate([raster, next_raster], axis=0)
                raster[raster_counter, int(ev["p"]), ev["y"], ev["x"]] += 1

        raster_list.append(raster)

    optim_step = max([len(i) for i in raster_list])
    for i, it in enumerate(raster_list):
        if (optim_step - len(it)):
            raster_list[i] = np.concatenate([it, np.zeros((optim_step - len(it), 2, y, x))])

    return raster_list



