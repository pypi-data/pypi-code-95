from enum import Enum
import cv2
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from halib import filesys


class VideoResolution(Enum):
    VR480p = '720x480'
    VR576p = '1280x720'
    VR720p_hd = '1280x720'
    VR1080p_full_hd = '1920x1080 '
    VR4K_uhd = '3840x2160'
    VR8K_uhd = '7680x4320'

    def __str__(self):
        return '%s' % self.value


def get_video_resolution_size(video_resolution):
    separator = 'x'
    resolution_str = str(video_resolution)
    info_arr = resolution_str.split(separator)
    width, height = int(info_arr[0]), int(info_arr[1])
    return width, height


def get_videos_by_resolution(directory, video_resolution,
                             video_ext='mp4', include_better=True):
    video_paths = filesys.filter_files_by_extension(directory, video_ext)
    filtered_video_paths = []
    for path in video_paths:
        vid = cv2.VideoCapture(path)
        height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        valid = False
        video_width, video_height = get_video_resolution_size(video_resolution)
        if not include_better:
            if width == video_width and height == video_height:
                valid = True
        else:
            if width >= video_width and height >= video_height:
                valid = True

        if valid:
            filtered_video_paths.append(path)
    return filtered_video_paths


# time in seconds
def trim_video(source, destination, start_time, end_time):
    ffmpeg_extract_subclip(source, start_time, end_time, targetname=destination)
