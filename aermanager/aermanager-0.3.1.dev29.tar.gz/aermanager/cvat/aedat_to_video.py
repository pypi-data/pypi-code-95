from aermanager.dataset_generator import dataset_content_generator

import numpy as np
import os


def remove_extension(file_path: str):
    return os.path.splitext(file_path)[0]


def normalize_frames(frames):
    normalized_frames = frames.sum(axis=1)

    max_per_frame = normalized_frames.max(axis=2).max(axis=1)
    max_per_frame[max_per_frame == 0] = 1

    normalized_frames = normalized_frames / \
        max_per_frame[:, np.newaxis, np.newaxis]

    return (255 * normalized_frames).astype('uint8')


def aedat_convert_to_video(file_path: str, **kwargs):

    assert os.path.exists(file_path), "The specified path doesn't exist!"
    assert os.path.isfile(file_path), "The specified path is not a file!"
    assert 'time_window' in kwargs, "time_window must be used during the video generation!"
    assert not 'spike_count' in kwargs, "spike_count must be NOT used during the video generation!"

    import imageio_ffmpeg

    video_name = remove_extension(file_path)+'.mp4'

    _, frames, _ = dataset_content_generator(file_path, **kwargs)

    normalized_frames = normalize_frames(frames)

    assert len(normalized_frames.shape) == 3

    size = (normalized_frames.shape[2], normalized_frames.shape[1])

    writer = imageio_ffmpeg.write_frames(
        video_name, size=size, pix_fmt_in='gray', quality=10.0, fps=30, macro_block_size=1)

    # Seed the generator with None at first.
    # Check project README on Github: https://github.com/imageio/imageio-ffmpeg

    writer.send(None)

    writer.send(normalized_frames.copy(order='C'))

    writer.close()
