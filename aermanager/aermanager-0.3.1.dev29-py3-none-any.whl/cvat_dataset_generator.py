import h5py
import warnings
from tqdm import tqdm
from pathlib import Path
from typing import Optional, Tuple, Callable, Union
from aermanager.parsers import parse_aedat4
from aermanager.annotate_aedat import per_frame_labels
from aermanager.cvat.parser import parse_labels_from_file
from aermanager.cvat.load_annotations import load_labelled_tracked_rois
from aermanager.dataset_generator import dataset_content_generator, _get_md5
from os import listdir
import numpy as np


def save_to_annotated_dataset(sliced_xytp,
                              frames,
                              bins,
                              destination_path,
                              labels_lut,
                              roi_id_to_label: Optional[dict] = None,
                              compression: Optional[str] = None):

    path = Path(destination_path)
    path.mkdir(parents=True, exist_ok=True)
    inverse_lut = {v: k for k, v in labels_lut.items()}

    for i, slc in enumerate(sliced_xytp):
        file_name = path / f"{i}.h5"

        with h5py.File(file_name, 'w') as F:

            if roi_id_to_label:
                F.create_dataset("rois/id", data=[*roi_id_to_label.keys()])
                F.create_dataset("rois/label",  data=[*roi_id_to_label.values()])

            F.create_dataset("labels_lut/id", data=[*labels_lut.keys()])
            F.create_dataset("labels_lut/label", data=[*labels_lut.values()])

            F.create_dataset('frame', data=frames[i], compression=compression)
            F.create_dataset('frame_size', data=frames[i].shape, compression=compression)
            F.create_dataset('label', data=per_frame_labels(slc, inverse_lut), compression=compression)
            F.create_dataset('spikes/t', data=slc['t'], compression=compression)
            F.create_dataset('spikes/x', data=slc['x'], compression=compression)
            F.create_dataset('spikes/y', data=slc['y'], compression=compression)
            F.create_dataset('spikes/p', data=slc['p'], compression=compression)
            F.create_dataset('spikes/id', data=slc['id'], compression=compression)
            F.create_dataset('bins/x', data=bins[1])
            F.create_dataset('bins/y', data=bins[0])


def load_labels_lut(file_path: str):
    with h5py.File(file_path, 'r') as F:
        assert 'labels_lut/id' in F, "Labels LUT keys are missing!"
        assert 'labels_lut/label' in F, "Labels LUT values are missing!"

        return dict(zip(F['labels_lut/id'], F['labels_lut/label']))


def load_frame_shape(file_path: str):
    with h5py.File(file_path, 'r') as F:
        assert 'frame_size' in F, "Frame size is missing!"

        return tuple(F['frame_size'])


def load_rois_lut(file_path: str):
    with h5py.File(file_path, 'r') as F:
        assert 'rois/id' in F, "'rois/id' is missing from file!"
        assert 'rois/label' in F, "'rois/label' is missing from file!"

        return dict(zip(F['rois/id'], F['rois/label']))


def load_annotated_slice(file_path: str):
    with h5py.File(file_path, 'r') as F:

        assert 'label' in F, "Labels are missing!"
        frame_labels = list(F['label'])

        assert 'spikes/x' in F, "'spikes/x' is missing from file!"
        assert 'spikes/y' in F, "'spikes/y' is missing from file!"
        assert 'spikes/t' in F, "'spikes/t' is missing from file!"
        assert 'spikes/p' in F, "'spikes/p' is missing from file!"
        assert 'spikes/id' in F, "'spikes/id' is missing from file!"

        events_struct = [("x", np.uint16), ("y", np.uint16), ("t", np.uint64), ("p", np.bool), ("id", np.float)]

        frame_events = np.empty(len(F['spikes/x']), dtype=events_struct)

        frame_events['x'] = F['spikes/x']
        frame_events['y'] = F['spikes/y']
        frame_events['t'] = F['spikes/t']
        frame_events['p'] = F['spikes/p']
        frame_events['id'] = F['spikes/id']

        return frame_events, frame_labels


def gen_annotated_dataset_from_list(
        event_files: list,
        labels: list,
        destination_path,
        compression: Optional[str] = None,
        crop_size: Optional[Tuple[Tuple]] = None,
        hot_pixel_frequency: Optional[float] = None,
        time_window: Optional[int] = None,
        spike_count: Optional[int] = None,
        parser: Union[Callable, str] = parse_aedat4, ):

    assert len(event_files) == len(labels), "The event list size is different from the label list size!"

    destination_path = Path(destination_path)
    destination_path.mkdir(parents=True, exist_ok=True)

    for fname, label in tqdm(zip(event_files, labels)):

        labels_lut = parse_labels_from_file([*label.values()][0])

        hash_code = _get_md5(fname)

        sliced_xytp, frames, bins_yx = dataset_content_generator(
            fname,
            crop_size=crop_size,
            hot_pixel_frequency=hot_pixel_frequency,
            time_window=time_window,
            spike_count=spike_count,
            tags_file_path=label.get('tags_file', None),
            rois_file_path=label.get('rois_file', None),
            parser=parser,
        )

        name = (Path(fname).with_suffix("").name + "_" + hash_code[:5])
        folder_path = destination_path / name

        if folder_path.exists():
            warnings.warn(f"Folder {folder_path} already exists", stacklevel=2)

        save_to_annotated_dataset(sliced_xytp, frames,
                                  bins=bins_yx,
                                  destination_path=folder_path,
                                  labels_lut=labels_lut,
                                  roi_id_to_label=load_labelled_tracked_rois(label.get('rois_file', None)),
                                  compression=compression)
