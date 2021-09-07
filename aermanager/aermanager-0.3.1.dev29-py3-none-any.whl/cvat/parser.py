from itertools import count
from lxml import etree


def parse_task_meta_information(root):

    tasks = root.xpath('//task')

    assert len(tasks) == 1, 'One annotation task per video file is supported!'

    frame_count = tasks[0].find('size').text
    height = tasks[0].find('original_size').find('height').text
    width = tasks[0].find('original_size').find('width').text

    return (int(frame_count), int(height), int(width))


def _parse_labels(root):
    for label in root.xpath('///label'):
        yield label.find('name').text


def parse_labels(root):
    label_names = ['__Empty_Default__'] + list(_parse_labels(root))
    return dict(zip(label_names, count()))


def parse_labels_from_file(file_path: str):
    return parse_labels(etree.parse(file_path))


def parse_tags(root):
    for frame in root.xpath('//image'):
        id = int(frame.attrib['id'])

        for tag in frame.xpath('tag'):
            yield id, tag.attrib['label']
