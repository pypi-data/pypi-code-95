"""
Created on 2020.07.30
:author: Felix Soubelet

Script to add a whiteframe to my pictures
"""

from pathlib import Path
from typing import List, Tuple, Union

from joblib import Parallel, delayed
from loguru import logger
from PIL import Image, ImageFile, ImageOps

from colorframe.utils import timeit

ImageFile.LOAD_TRUNCATED_IMAGES = True  # Prevent PIL from crashing on 'image file is truncated'


def process_directory_of_images(
    directory_path: Path, border: Union[int, Tuple[int, int]], color: str = "white"
) -> None:
    """
    Add a whiteframe border to all valid images detected in the provided directory.

    Args:
        directory_path: a pathlib.Path object to a directory location.
        border: size of the border to be applied. If integer, the same size will be applied to
                all edges. If tuple, the first value is used for the vertical edges borders,
                and the second value for the horizontal edges borders.
        color: string, the keyword for the desired border color. Default 'white'.

    Returns:
        Nothing.
    """
    if _log_directory_status(directory_path) != 0:
        images_to_process: List[Path] = sorted(
            set(
                list(directory_path.rglob("*.jpg"))
                + list(directory_path.rglob("*.JPG"))
                + list(directory_path.rglob("*.jpeg"))
                + list(directory_path.rglob("*.JPEG"))
            )
        )
        with timeit(
            lambda spanned: logger.success(
                f"Treated {len(images_to_process)} files in '{directory_path.absolute()}'"
                f" in {spanned:.4f} seconds"
            )
        ):
            _ = Parallel(n_jobs=-1)(
                delayed(add_colorframe_to_image)(image_path, border, color)
                for image_path in images_to_process
            )  # overhead of Parallel isn't big enough on a few files to justify not using it ;)


def _log_directory_status(checked_path: Path) -> int:
    """
    Checks the validity of the provided path as a directory, while logging accordingly.

    Args:
        checked_path: a pathlib.Path object to a directory location.

    Returns:
        0 if the path is not a directory or is inexistent, 1 otherwise.
    """
    if not checked_path.is_dir():
        logger.error(f"Provided path at '{checked_path}' is not a valid directory")
        return 0
    else:
        logger.info(f"Treating directory at '{checked_path.absolute()}'")
        return 1


@logger.catch(message="Possible PIL internal exceptions here")
def add_colorframe_to_image(
    image_path: Path, border: Union[int, Tuple[int, int]], color: str = "white"
) -> None:
    """
    Add the specified whiteframe border to the provided image, and output the result to a new file.

    Args:
        image_path: a pathlib.Path object to the image file's location.
        border: size of the border to be applied. If integer, the same size will be applied to
                all edges. If tuple, the first value is used for the vertical edges borders,
                and the second value for the horizontal edges borders.
        color: string, the keyword for the desired border color. Default 'white'.

    Returns:
        Nothing, works on the image and exits.
    """
    if _log_image_file_status(image_path) == 1 and (
        isinstance(border, int) or isinstance(border, tuple)
    ):
        output_file = Path("outputs") / (image_path.stem + f"_{color}framed" + image_path.suffix)
        image = Image.open(image_path)

        try:
            bordered_image: Image = ImageOps.expand(image, border, fill=color)
            bordered_image.save(output_file)
        except OSError as pillow_error:  # the strange 'image file is truncated' on big files
            logger.error(
                f"An error happened during PIL handling of the image at '{image_path.absolute()}'"
            )
        logger.info(f"Added border to image at '{image_path.absolute()}'")


def _log_image_file_status(checked_path: Path) -> int:
    """
    Checks the validity of the provided path as a jpg or jpeg file, while logging accordingly.

    Args:
        checked_path: a pathlib.Path object to a location.

    Returns:
        0 if the path is not an image, 1 otherwise.
    """
    if not checked_path.is_file():
        logger.error(f"Provided path at '{checked_path}' is not a valid file")
        return 0
    elif checked_path.suffix.lower() not in (".jpg", ".jpeg", ".png"):
        logger.error(f"File at '{checked_path}' is not an image")
        return 0
    else:
        logger.trace(f"Treating image at '{checked_path.absolute()}'")
        return 1
