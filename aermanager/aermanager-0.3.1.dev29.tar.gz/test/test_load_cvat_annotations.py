from aermanager.cvat.load_annotations import load_annotations
from aermanager.dataset_generator import dataset_content_generator
from aermanager.cvat.parser import parse_labels
from lxml import etree

from aermanager.cvat.load_annotations import *
from aermanager.cvat.parser import *

import numpy as np
import pytest
import os

test_dir_path = os.path.dirname(os.path.realpath(__file__))
video_annotations_file_path = test_dir_path + '/dummy_video_annotations.xml'
image_annotations_file_path = test_dir_path + '/dummy_image_annotations.xml'


def unordered_np_array_compare(a, b):
    return np.array_equal(np.sort(a.flat), np.sort(b.flat))


def test_load_xml_labels():
    root_cvat_for_video = etree.parse(video_annotations_file_path)
    root_cvat_for_images = etree.parse(image_annotations_file_path)

    labels_v = parse_labels(root_cvat_for_video)
    labels_i = parse_labels(root_cvat_for_images)

    assert labels_v == labels_i, "Labels should be equal for CVAT for Video and for Images XML files."

    assert labels_v['__Empty_Default__'] == 0
    assert labels_v['Pen'] == 1
    assert labels_v['Rabbit'] == 2
    assert labels_v['Box'] == 3
    assert labels_v['Mug'] == 4
    assert labels_v['Whole_frame_tag_1'] == 5
    assert labels_v['whole_frame_tag_2'] == 6


def test_annotate_no_vertices_roi_throws():
    with pytest.raises(IndexError):
        vertices = np.empty((1, 1))
        _, _ = roi_coordinates(vertices)


def test_parse_bounding_box():
    class StubBoundingBox:
        def __init__(self, xtl, ytl, xbr, ybr):
            self.attrib = {'ytl': ytl, 'ybr': ybr, 'xtl': xtl, 'xbr': xbr}

    bb = StubBoundingBox(0, 0, 6, 6)  # Create a StubBoundingBox of area 36
    vertices = parse_bounding_box(bb)

    assert (0, 0) in vertices
    assert (6, 0) in vertices
    assert (6, 6) in vertices
    assert (0, 6) in vertices


def test_parse_polygon():
    class StubPolygon:
        def __init__(self, str):
            self.attrib = {'points': str}

    polygon = StubPolygon("0.3,1.9;2.3,3.4;4.0,5.1")

    vertices = parse_polygon(polygon)

    assert isinstance(vertices, np.ndarray)

    assert vertices.shape == (3, 2)

    assert np.all(vertices[0] == [0, 1])
    assert np.all(vertices[1] == [2, 3])
    assert np.all(vertices[2] == [4, 5])


def test_load_tags():
    root = etree.parse(image_annotations_file_path)
    labels = parse_labels(root)
    tags = parse_task_tags(root, labels)

    assert len(tags) == 195
    assert unordered_np_array_compare(tags.label.unique(), np.array([5, 6]))


def test_load_annotations():
    root = etree.parse(video_annotations_file_path)
    labels = parse_labels(root)
    annotations = parse_task_annotations(root, labels)

    assert unordered_np_array_compare(annotations.id.unique(), np.array([0, 1, 2, 3]))
    assert unordered_np_array_compare(annotations.label.unique(), np.array([1, 2, 3, 4]))


def test_roi_id_to_label_lut():
    root = etree.parse(video_annotations_file_path)
    lut = roi_id_to_label_lut(root)

    assert lut == {0: 'Mug', 1: 'Rabbit', 2: 'Box', 3: 'Pen'}


def test_load_labelled_tracked_rois():

    d = load_labelled_tracked_rois(image_annotations_file_path)
    assert not bool(d)

    d = load_labelled_tracked_rois(video_annotations_file_path)
    assert bool(d)
    assert d[0] == 'Mug'
    assert d[1] == 'Rabbit'
    assert d[2] == 'Box'
    assert d[3] == 'Pen'


def test_load_labelled_tracked_rois_none_input():
    assert load_labelled_tracked_rois(None) is None
