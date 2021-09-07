from aermanager.cvat.load_annotations import load_annotations, load_tags
from typing import Optional

import itertools

import pandas as pd
import numpy as np


def _frame_from_timestamp(t_min, t_max, f_min, f_max):
    return lambda timestamps: np.interp(timestamps, [t_min, t_max], [0, f_max - 1]).astype(int)


def frame_from_timestamp(events, f_max: int):
    assert f_max != 0, 'The number of annotated frames is zero!'

    t_min = events[0]['t'][0] if (type(events) == list) else events['t'][0]
    t_max = events[-1]['t'][-1] if (type(events) == list) else events['t'][-1]

    assert t_max > t_min, 'The time interval for the given sliced_xytp is negative! Check data layout!'

    return _frame_from_timestamp(t_min, t_max, f_min=0, f_max=f_max)


def label_events(events, annotations, merge_on, drop):

    annotated_events = pd.merge(events, annotations, indicator=True, how='left', on=merge_on).drop(columns=drop)

    unlabelled = annotated_events.query('_merge == "left_only"').drop(
        columns=['_merge', 'label', 'id'], errors='ignore')

    labelled = annotated_events.query('_merge == "both"').drop(columns='_merge')

    return labelled, unlabelled


def _annotate_events(events, rois=pd.DataFrame(columns=['frame', 'x', 'y']), tags=pd.DataFrame(columns=['frame'])):
    assert not (rois.empty and tags.empty), "Both ROIs annotatons and tags annotations are empty!"

    roi_levents, roi_ulevents = label_events(events, rois, merge_on=['frame', 'x', 'y'], drop=['frame'])

    tag_levents, tag_ulevents = label_events(events, tags, merge_on=['frame'], drop=['frame'])

    unlabelled = pd.merge(roi_ulevents, tag_ulevents, how='inner')

    annotated_events = pd.concat([roi_levents, tag_levents, unlabelled])

    annotated_events.sort_values(by=['t'], inplace=True)
    
    annotated_events.reset_index(drop=True, inplace=True)

    dtypes = annotated_events.dtypes

    results = np.array([tuple(x) for x in annotated_events.values], dtype=list(zip(dtypes.index, dtypes)))

    return results[['x', 'y', 't', 'p', 'label', 'id']]


def annotate_events(events, rois_annotation_path: Optional[str] = None, tags_annotation_path: Optional[str] = None):

    assert rois_annotation_path or tags_annotation_path, "Both ROIs and tags annotations files are missing!"

    kwargs = dict()

    if rois_annotation_path:
        frame_count, rois_annotations = load_annotations(rois_annotation_path)
        kwargs['rois'] = rois_annotations

    if tags_annotation_path:
        frame_count, frame_tags = load_tags(tags_annotation_path)
        kwargs['tags'] = frame_tags

    timestamp_interpolation = frame_from_timestamp(events, frame_count)

    events_df = pd.DataFrame(events)

    events_df.insert(0, 'frame', timestamp_interpolation(events['t']))

    kwargs['events'] = events_df.drop_duplicates()

    return _annotate_events(**kwargs)


def per_frame_labels(frame_events, labels_inverse_lut):
    assert type(frame_events) == np.ndarray
    assert 'label' in frame_events.dtype.names

    frame_labels = np.unique(frame_events['label'])

    return [labels_inverse_lut[l] for l in frame_labels[~np.isnan(frame_labels)]]
