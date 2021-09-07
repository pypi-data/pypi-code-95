from aermanager.cvat.parser import parse_labels, parse_tags, parse_task_meta_information

from lxml import etree
from skimage.draw import polygon

import pandas as pd
import numpy as np
import math


def roi_coordinates(vertices: np.ndarray):
    return polygon(vertices[:, 1], vertices[:, 0])


def bounding_boxes_vertices(ytl, xtl, ybr, xbr):
    return np.array([(xtl, ytl), (xbr, ytl), (xbr, ybr), (xtl, ybr)]).astype(int)


def polygon_vertices(vertices: str):

    def parse_coords(vertex):
        coords = vertex.split(',')
        return (float(coords[0]), float(coords[1]))

    coords = [parse_coords(vertex) for vertex in vertices.split(';')]

    return np.array(coords).astype(int)


def parse_bounding_box(bounding_box):

    ytl = math.floor(float(bounding_box.attrib['ytl']))
    xtl = math.floor(float(bounding_box.attrib['xtl']))

    ybr = math.ceil(float(bounding_box.attrib['ybr']))
    xbr = math.ceil(float(bounding_box.attrib['xbr']))

    return bounding_boxes_vertices(ytl, xtl, ybr, xbr)


def parse_polygon(polygon):
    return polygon_vertices(polygon.attrib['points'])


def annotate_roi(roi, vertices_parser, id, label):

    annotation_dtype = [('frame', np.uint64),
                        ('x', np.uint16),
                        ('y', np.uint16),
                        ('label', np.uint8),
                        ('id', np.uint32)]

    frame = int(roi.attrib['frame'])

    vertices = vertices_parser(roi)

    ycoords, xcoords = roi_coordinates(vertices)

    annotation_size = len(ycoords)

    ann = np.empty((annotation_size,), dtype=annotation_dtype)

    ann['frame'], ann['id'], ann['label'], ann['x'], ann['y'] = frame, id, label, xcoords, ycoords

    return ann


def roi_id_to_label_lut(root):
    return {int(track.attrib['id']): track.attrib['label'] for track in root.xpath('track')}


def parse_task_annotations(root, labels):

    annotations = []

    for tracked_object in root.xpath('track'):

        label = labels[tracked_object.attrib['label']]
        id = tracked_object.attrib['id']

        for bb in tracked_object.xpath('box'):
            annotations.append(annotate_roi(bb, parse_bounding_box, id, label))

        for polygon in tracked_object.xpath('polygon'):
            annotations.append(annotate_roi(polygon, parse_polygon, id, label))

    return pd.DataFrame(np.concatenate(annotations)).drop_duplicates()


def parse_task_tags(root, labels):
    tags = [(id, labels[tag]) for id, tag in parse_tags(root)]
    return pd.DataFrame(tags, columns=['frame', 'label']).drop_duplicates()


def parse_xml_annotations(file_path, parsing_function):
    root = etree.parse(file_path)
    frame_count, _, _ = parse_task_meta_information(root)
    return frame_count, parsing_function(root, parse_labels(root))


def load_annotations(rois_file_path: str):
    return parse_xml_annotations(file_path=rois_file_path,
                                 parsing_function=parse_task_annotations)


def load_tags(tags_file_path: str):
    return parse_xml_annotations(file_path=tags_file_path,
                                 parsing_function=parse_task_tags)


def _load_labelled_tracked_rois(root):
    return {int(t.attrib['id']): t.attrib['label'] for t in root.xpath('track')}


def load_labelled_tracked_rois(rois_file_path: str):
    if rois_file_path is None:
        return None

    root = etree.parse(rois_file_path)
    return _load_labelled_tracked_rois(root)
