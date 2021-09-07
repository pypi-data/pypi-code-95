from aermanager.aerparser import load_events_from_file
from aermanager import preprocess
import numpy as np
from pathlib import Path

TEST_FILE = Path(__file__).parent / "data" / "class2" / "data_sample.aedat4"


def test_slice_by_time():
    shape, xytp = load_events_from_file(TEST_FILE)
    assert(shape == (240, 320))
    time_window = 10000
    sliced_xytp = preprocess.slice_by_time(xytp, time_window)  # 10ms
    assert len(sliced_xytp) > 0
    for slice in sliced_xytp:
        tw_actual = slice["t"][-1] - slice["t"][0]
        assert(tw_actual <= time_window)

def test_overtime():
    shape, xytp = load_events_from_file(TEST_FILE)
    assert(shape == (240, 320))
    time_window = 100e6
    sliced_xytp = preprocess.slice_by_time(xytp, time_window)
    assert len(sliced_xytp) == 1
    for slice in sliced_xytp:
        tw_actual = slice["t"][-1] - slice["t"][0]
        assert(tw_actual <= time_window)

def test_slice_by_time_with_overlap():
    shape, xytp = load_events_from_file(TEST_FILE)
    assert (shape == (240, 320))
    time_window = 10000
    overlap = 5000
    sliced_xytp = preprocess.slice_by_time(xytp, time_window, overlap)
    assert len(sliced_xytp) > 0
    for slice in sliced_xytp:
        tw_actual = slice[-1]["t"] - slice[0]["t"]
        assert tw_actual // time_window <= 1

def test_slice_by_count_in_exact():
    shape, xytp = load_events_from_file(TEST_FILE)
    assert(shape == (240, 320))
    spk_count = 1000
    sliced_xytp = preprocess.slice_by_count(xytp, spk_count)
    assert len(sliced_xytp) > 0
    for i, slice in enumerate(sliced_xytp):
        count_actual = len(slice)
        assert(count_actual == spk_count)
    assert(len(xytp) - sum([len(slice) for slice in sliced_xytp]) < spk_count)

def test_slice_by_count_exact():
    shape, xytp = load_events_from_file(TEST_FILE)
    spk_count = 1000
    xytp = xytp[:spk_count * int(len(xytp) / spk_count)]
    assert(shape == (240, 320))
    sliced_xytp = preprocess.slice_by_count(xytp, spk_count)
    assert len(sliced_xytp) > 0
    for i, slice in enumerate(sliced_xytp):
        count_actual = len(slice)
        assert(count_actual == spk_count)
    assert(len(xytp) - sum([len(slice) for slice in sliced_xytp]) < spk_count)

def test_overcount():
    shape, xytp = load_events_from_file(TEST_FILE)
    assert(shape == (240, 320))
    spk_count = 100e6
    sliced_xytp = preprocess.slice_by_count(xytp, spk_count)
    assert len(sliced_xytp) == 1
    assert(len(xytp) - sum([len(slice) for slice in sliced_xytp]) < spk_count)

def test_accumulate_frames_spike_count():
    shape, xytp = load_events_from_file(TEST_FILE)
    spk_count = 1000
    sliced_xytp = preprocess.slice_by_count(xytp, spk_count)
    assert len(sliced_xytp) > 0
    frames = preprocess.accumulate_frames(
        sliced_xytp, np.arange(shape[0] + 1), np.arange(shape[1] + 1))
    for f in frames:
        assert(f.shape == (2, *shape))
        assert (f.sum() == spk_count)


def test_accumulate_frames_time_window():
    shape, xytp = load_events_from_file(TEST_FILE)
    time_window = 50000
    sliced_xytp = preprocess.slice_by_time(xytp, time_window)[:-1]
    assert len(sliced_xytp) > 0
    frames = preprocess.accumulate_frames(
        sliced_xytp, np.arange(shape[0] + 1), np.arange(shape[1] + 1))
    for i, f in enumerate(frames):
        assert(f.shape == (2, *shape))
        assert (f.sum() == len(sliced_xytp[i]))


def test_crop_events_obvious():
    shape, xytp = load_events_from_file(TEST_FILE)
    cropped_xytp, new_shape = preprocess.crop_events(xytp, input_shape=shape,
                                                     crop_size=((0, 0), (0, 0)))
    assert(len(cropped_xytp) == len(xytp))
    assert(new_shape == shape)


def test_crop_events():
    shape, xytp = load_events_from_file(TEST_FILE)
    print(shape)
    cropped_xytp, new_shape = preprocess.crop_events(xytp, input_shape=shape,
                                                     crop_size=((10, 50), (5, 7)))
    assert(len(cropped_xytp) != len(xytp))
    # Check width
    assert(cropped_xytp["x"].max() == shape[1] - 50 - 10 - 1)
    assert(cropped_xytp["x"].min() == 0)
    # Check height
    assert(cropped_xytp["y"].max() == shape[0] - 5 - 7 - 1)
    assert(cropped_xytp["y"].min() == 0)

    assert new_shape == ((shape[0] - 5 - 7), (shape[1] - 50 - 10))


def test_crop_frame():
    shape, xytp = load_events_from_file(TEST_FILE)
    spk_count = 1000
    sliced_xytp = preprocess.slice_by_count(xytp, spk_count)
    assert len(sliced_xytp) > 0
    frames = preprocess.accumulate_frames(
        sliced_xytp, np.arange(shape[0] + 1), np.arange(shape[1] + 1))
    for f in frames:
        frame_cropped = preprocess.crop_frame(f, crop_size=((10, 50), (5, 7)))
        assert(frame_cropped.shape == (2, shape[0] - 5 - 7, shape[1] - 10 - 50))


def test_filter_hot_pixels():
    shape, xytp = load_events_from_file(TEST_FILE)
    xytp_filtered = preprocess.filter_hot_pixels(xytp, shape=shape, hot_pixel_frequency=1000)
    assert(len(xytp_filtered) <= len(xytp))

def test_create_hybrid_uniform_raster():
    shape, xytp = load_events_from_file(TEST_FILE)
    list_xytp = preprocess.slice_by_time(xytp, 10e3)
    hybrid_raster = preprocess.create_hybrid_uniform_raster(list_xytp, shape)

    assert [item.max() == 1. for item in hybrid_raster]

test_create_hybrid_uniform_raster()