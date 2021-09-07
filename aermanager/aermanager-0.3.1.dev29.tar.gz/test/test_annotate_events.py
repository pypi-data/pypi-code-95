from aermanager.annotate_aedat import *

import numpy as np
import pandas as pd
import os
import pytest


test_dir_path = os.path.dirname(os.path.realpath(__file__))
label_file_path = test_dir_path + '/dummy_video_annotations.xml'
label_file_path = test_dir_path + '/dummy_video_annotations.xml'


def stub_events_dataframe():
    events = np.zeros((100,), dtype=[('frame', int), ('x', int), ('y', int), ('t', int), ('p', bool)])

    events['x'] = events['y'] = events['t'] = events['frame'] = np.arange(0, 100)
    events['p'] = np.arange(0, 100) % 2

    return pd.DataFrame(events)


def stub_roi_annotations_dataframe():
    annotation_dtype = [('frame', int), ('x', int), ('y', int), ('label', int), ('id', int)]

    annotations = np.zeros((50,), dtype=annotation_dtype)

    annotations['frame'] = annotations['x'] = annotations['y'] = np.arange(0, 50)
    annotations['label'] = np.arange(0, 50) % 5
    annotations['id'] = np.arange(0, 50) % 10

    return pd.DataFrame(annotations)


events = stub_events_dataframe()
annotations = stub_roi_annotations_dataframe()


def test_timestamp_to_frame_interpolation():

    from aermanager.annotate_aedat import _frame_from_timestamp

    interpolation_fcn = _frame_from_timestamp(t_min=0, t_max=100, f_min=0, f_max=50)

    input = np.arange(0, 100)
    output = interpolation_fcn(input)

    assert (np.unique(output) == np.arange(0, 49)).all()


def test_label_events_throws_on_missing_columns():
    with pytest.raises(KeyError):
        _, _ = label_events(events, annotations, merge_on=['frame', 'x', 'y'], drop=['missing_column'])

    with pytest.raises(KeyError):
        _, _ = label_events(events, annotations, merge_on=['missing_column', 'x', 'y'], drop=['frame'])


def test_label_roi_events():
    labelled, unlabelled = label_events(events, annotations, merge_on=['frame', 'x', 'y'], drop=['frame'])

    assert len(events) == (len(labelled) + len(unlabelled))


def test_label_roi_events_empty_annotations_doesent_throw():
    labelled, unlabelled = label_events(events, pd.DataFrame(
        columns=['frame', 'x', 'y']), merge_on=['frame', 'x', 'y'], drop=['frame'])

    assert len(labelled) == 0
    assert len(unlabelled) == len(events)

    labelled, unlabelled = label_events(events, pd.DataFrame(columns=['frame']), merge_on=['frame'], drop=['frame'])

    assert len(labelled) == 0
    assert len(unlabelled) == len(events)


def _stub_labelled_events(size, labels_num):
    events = np.empty((size,), dtype=[('label', float)])

    for i in range(0, size):
        events['label'][i] = i % (labels_num + 1)

    nans = np.empty((size,), dtype=[('label', float)])
    nans[:] = np.nan

    return np.hstack((events, nans))


def test_per_frame_labels():
    stub_events = _stub_labelled_events(size=100, labels_num=5)
    inverse_label_lut = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F'}
    results = per_frame_labels(stub_events, inverse_label_lut)
    expected = inverse_label_lut.values()

    assert all(val in results for val in expected)
