from aermanager.preprocess import accumulate_frames
import numpy as np


def init_data(channels=False):
    """
    Init data for testing:
    evets_struct: numpy structure for aer data
    xytp: events data as numpy in the format of evets_struct
    expectd_output: events count in a 4d image (batch_id, dimontion_id, x, y)
    """

    events_struct = [("x", np.uint16), ("y", np.uint16), ("t", np.uint64), ("p", bool)]

    x = [0, 1, 0, 1, 2, 2, 2, 5]
    y = [0, 0, 1, 1, 2, 2, 5, 5]
    t = [0, 1, 2, 3, 7, 8, 9, 10]
    p = [False, True, False, True, False, True, True, True]

    xytp = np.fromiter(zip(x, y, t, p), dtype=events_struct)

    expected_output = np.array(
        [
            [
                [1, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
            ],
            [
                [0, 1, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 1],
            ]
        ]
    )
    if not channels:
        expected_output = expected_output.sum(0)[np.newaxis]
    return events_struct, xytp, expected_output


def test_accumulate_image():
    _, xytp, expected_output = init_data(channels=True)
    output_res = expected_output.shape[-2:]

    out = accumulate_frames([xytp], range(output_res[0] + 1), range(output_res[1] + 1))
    assert np.allclose(expected_output, out[0])


def test_spktrain_count():
    from aermanager.preprocess import slice_by_count

    events_struct, xytp, expected_output = init_data()
    exp_spk = np.array(
        [
            np.array([(0, 0, 0, False), (1, 0, 1, True), (0, 1, 2, False)], dtype=events_struct),
            np.array([(1, 1, 3, True), (2, 2, 7, False), (2, 2, 8, True)], dtype=events_struct),
        ]
    )

    out = slice_by_count(xytp, spike_count=3)

    assert len(out) == len(exp_spk)
    for i in range(len(out)):
        assert (out[i] == exp_spk[i]).all()
    assert (exp_spk == out).all()


def test_crop():
    """
    create a dummy aedatconvert, conv
    test the event output as count of conv.accumulate
    crop to (None, 3) on dim x and (1, None) on dim y
    """
    from aermanager.preprocess import crop_events

    events_struct, xytp, expected_output = init_data(channels=True)
    crop = [[0, 2], [1, 0]]
    exp_out_crop = expected_output[:, 1:, :4]

    cropped_xytp, new_shape = crop_events(xytp, input_shape=(6, 6), crop_size=crop)
    out = accumulate_frames([cropped_xytp], range(new_shape[0] + 1), range(new_shape[1] + 1))

    assert np.allclose(exp_out_crop, out)
#
#
# def test_low_res():
#     """
#     create a dummy aedatconvert, conv
#     test the event output as count of conv.accumulate
#     set resized resolution
#     """
#     import numpy as np
#     from aermanager import AedatConvert
#     from .utils import init_data
#
#     events_struct, xytp, expected_output = init_data()
#     output_res = (3, 3)
#     exp_out_lowres = np.array([[[4, 0, 0], [0, 2, 1], [0, 0, 1]]])
#
#     conv = AedatConvert(
#         data_list_file="dummy_file_list.txt",
#         accumulation_method="timeinterval",
#         accumulation_value=10,
#         output_resolution=output_res,
#     )
#
#     out, _ = conv.accumulate(xytp)
#     assert np.allclose(exp_out_lowres, out)
#


def test_slice_time_twochan():
    from aermanager.preprocess import slice_by_time

    events_struct, xytp, expected_output = init_data()
    output_res = (3, 3)
    exp_out_time = np.array([
        [
            [[2, 0, 0], [0, 0, 0], [0, 0, 0]],
            [[1, 0, 0], [0, 0, 0], [0, 0, 0]],
        ],
        [
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
            [[1, 0, 0], [0, 0, 0], [0, 0, 0]],
        ],
        [
            [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
            [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
        ]
    ])
    # axis conventions changed since we wrote this test.
    exp_out_time = np.swapaxes(exp_out_time, -1, -2)

    sliced_xytp = slice_by_time(xytp, time_window=3)
    out = accumulate_frames(sliced_xytp, bins_x=range(0, 7, 2), bins_y=range(0, 7, 2))

    assert out.shape == (3, 2, *output_res)
    assert np.allclose(exp_out_time, out)


def test_spike_accum_twochan():
    from aermanager.preprocess import slice_by_count

    events_struct, xytp, expected_output = init_data()
    output_res = (3, 3)
    exp_out_spike = np.array([
        [
            [
                [2, 0, 0],
                [0, 0, 0],
                [0, 0, 0]
            ],
            [
                [1, 0, 0],
                [0, 0, 0],
                [0, 0, 0]
            ]
        ],
        [
            [
                [0, 0, 0],
                [0, 1, 0],
                [0, 0, 0]
            ],
            [
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, 0]
            ]
        ]
    ])
    # axis conventions changed since we wrote this test.
    exp_out_spike = np.swapaxes(exp_out_spike, -1, -2)

    sliced_xytp = slice_by_count(xytp, spike_count=3)
    out = accumulate_frames(sliced_xytp, bins_x=range(0, 7, 2), bins_y=range(0, 7, 2))

    assert out.shape == (2, 2, *output_res)
    assert np.allclose(exp_out_spike, out)


def test_hotpixel():
    """
    create a dummy aedatconvert, conv
    test the event output as count of conv.accumulate
    remove hot pixel
    """
    from aermanager.preprocess import filter_hot_pixels

    events_struct, xytp, expected_output = init_data()
    output_res = (6, 6)
    exp_out_hotpixel = np.array(
        [
            [
                [1, 1, 0, 0, 0, 0],
                [1, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 1],
            ]
        ]
    )

    xyz = filter_hot_pixels(xytp, hot_pixel_frequency=0.15e6, shape=output_res)
    out = accumulate_frames([xyz], bins_y=range(7), bins_x=range(7)).sum(1, keepdims=True)

    assert np.allclose(exp_out_hotpixel, out[0])
