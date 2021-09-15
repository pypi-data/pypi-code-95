"""
Color bar
---------

Created on 2019.08.28
:author: Felix Soubelet

A little script for fun that will make a video file into a color bar image. The colors are
calculated from frames of the video according the a specified method. Enjoy.
"""
import shutil
import subprocess
from pathlib import Path

from loguru import logger
from PIL import Image

from movie_colorbar.generative_functions import (
    get_average_hsv,
    get_average_hue,
    get_average_lab,
    get_average_rgb,
    get_average_rgb_squared,
    get_average_xyz,
    get_kmeans_color,
    get_most_common_colors_as_rgb,
    get_quantized_color,
    get_resized_1px_rgb,
)

METHOD_ACTION_MAP: dict = {
    "rgb": get_average_rgb,
    "hsv": get_average_hsv,
    "hue": get_average_hue,
    "kmeans": get_kmeans_color,
    "common": get_most_common_colors_as_rgb,
    "xyz": get_average_xyz,
    "lab": get_average_lab,
    "rgbsquared": get_average_rgb_squared,
    "resize": get_resized_1px_rgb,
    "quantized": get_quantized_color,
}

VALID_VIDEO_EXTENSIONS = (
    ".webm",
    ".mkv",
    ".flv",
    ".vob",
    ".ogg",
    ".ogv",
    ".drc",
    ".gif",
    ".gifv",
    ".mng",
    ".avi",
    ".mov",
    ".qt",
    ".wmv",
    ".yuv",
    ".rm",
    ".rmvb",
    ".asf",
    ".amv",
    ".mp4",
    ".m4p",
    ".m4v",
    ".mpg",
    ".mp2",
    ".mpv",
    ".m4v",
    ".flv",
)


def extract_frames(movie_input_path: str, fps: int) -> list:
    """
    Runs ffmpeg to decompose the video file into stills.

    Args:
        movie_input_path:  Absolute path to the video file.
        fps: Number of frames to extract per second.

    Returns:
        list of absolute paths to all frames extracted (and stored in an intermediate folder).
    """
    logger.info("Extracting frames")
    images_directory = Path("images")

    if not images_directory.is_dir():
        logger.debug("Creating 'images' directory to store the video's frames")
        images_directory.mkdir()
    else:
        logger.error(
            "A directory named 'images' already exists, please remove it to avoid " "accidents"
        )
        raise IsADirectoryError("The 'images'  directory should not exist")

    logger.info(f"Running ffmpeg, extracting {fps} frames per second of video")
    command = ["ffmpeg", "-i", f"{movie_input_path}", "-vf", f"fps={fps}", "images/%05d.jpg"]
    _ = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    logger.debug("Gathering frames")
    all_images = [str(element) for element in Path("images").iterdir()]
    all_images.sort(key=lambda x: int(x[7:-4]))
    logger.info(f"Successfully extracted {len(all_images)} images from {movie_input_path}")
    return all_images


def get_images_colors(images_list: list, method: str) -> list:
    """
    Getting average color of each image through to the provided method.

    Args:
        images_list: list of absolute paths to all frames to process.
        method: string, method to apply to each image to get its average color.

    Returns:
        list of computed average color for all images, one tuple per image.
    """
    logger.info(f"Extracting colors from images, with method '{method}'")
    bar_colors = []
    for filename in images_list:
        image = Image.open(filename).resize((25, 25))
        average_image_color = METHOD_ACTION_MAP[method](image)
        bar_colors.append(average_image_color)
    return bar_colors


def create_colorbar(all_bar_colors: list) -> Image:
    """
    Create the colorbar from the computed average colors.

    Args:
        all_bar_colors: list of computed average color for all images, one tuple per image.

    Returns:
        a Pillow.Image instance, with the colors implemented as a colorbar.
    """
    logger.info("Creating colorbar from extracted images")
    bar_image = Image.new("RGB", (len(all_bar_colors), max([1, int(len(all_bar_colors) / 2.5)])))
    bar_full_data = [x for x in all_bar_colors] * bar_image.size[1]
    bar_image.putdata(bar_full_data)
    return bar_image


def _is_video(file_path_string: str = None):
    """
    Check that the file extension is a valid video format.

    Args:
        file_path_string: string, path to the file.

    Returns:
        True if the file is in a valid video format, False otherwise.
    """
    return Path(file_path_string).suffix.lower() in VALID_VIDEO_EXTENSIONS


def process_video(title: str, method: str, source_path: str, frames_per_second: int = 10) -> None:
    """
    Will populate a folder named `images` with every extracted image from the provided video,
    and create the color bar from those images. Deletes said folder afterwards.

    Args:
        title: string, name to give the intermediate directory.
        method: string, method to use to get the colors.
        source_path: string, absolute path to the video file.
        frames_per_second: integer, number of frames to extract per second of video. You'll want to
                           lower this parameter on longer videos.

    Returns:
        Nothing.
    """
    logger.info(f"Processing video at '{source_path}'")
    bars_directory = Path("bars")
    images = extract_frames(source_path, frames_per_second)
    bar_colors = get_images_colors(images, method)
    bar_image = create_colorbar(bar_colors)

    if not bars_directory.is_dir():
        logger.debug("'bars' directory is absent, it will be created")
        bars_directory.mkdir()

    if not (bars_directory / f"{title}").is_dir():
        logger.debug(f"'bars/{title}' directory is absent, it will be created")
        (bars_directory / f"{title}").mkdir()

    bar_image.save(f"bars/{title}/{Path(source_path).stem}_{method}.png")
    logger.success(f"Created bar at 'bars/{title}/{Path(source_path).stem}_{method}.png'")

    logger.info("Cleanup: removing 'images' directory")
    shutil.rmtree("images")


def process_dir(title: str, method: str, source_path: str, frames_per_second: int = 10) -> None:
    """
    Will process every video into the directory.

    Args:
        title: string, name to give the intermediate directory.
        method: string, method to use to get the colors.
        source_path: string, absolute path to the video file.
        frames_per_second: integer, number of frames to extract per second of video. You'll want to
                           lower this parameter on longer videos.

    Returns:
        Nothing.
    """
    logger.info("Provided path is a directory, now processing all videos")
    directory = Path(source_path)

    for file_path in sorted(directory.iterdir()):
        if _is_video(file_path):
            process_video(
                title=title,
                method=method,
                source_path=str(file_path),
                frames_per_second=frames_per_second,
            )
        else:
            logger.warning(f"File '{source_path}' is not a video, skipping")
