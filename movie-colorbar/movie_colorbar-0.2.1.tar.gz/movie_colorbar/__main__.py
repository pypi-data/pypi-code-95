"""
Running the tool from the commandline, if it is installed in your environment.
"""

import sys
from pathlib import Path

import typer
from loguru import logger

from movie_colorbar.color_bar import METHOD_ACTION_MAP, process_dir, process_video

app = typer.Typer()


@app.command()
def create(
    source_path: str = typer.Argument(
        ".",
        help="Location, relative or absolute, of the source video file to get the images from.",
    ),
    title: str = typer.Option("output", help="Name that will be given to the output directory.",),
    method: str = typer.Option(
        "rgbsquared",
        help="Method used to calculate the average color. Options are: 'rgb', 'hsv', 'hue', "
        "'kmeans', 'common', 'lab', 'xyz', 'rgbsquared', 'resize' and 'quantized'.",
    ),
    fps: int = typer.Option(10, help="Number of frames to extract per second of video footage.",),
    log_level: str = typer.Option(
        "info",
        help="The base console logging level. Can be 'debug', 'info', 'warning' and 'error'.",
    ),
) -> None:
    """Turn a video into a colorbar."""
    set_logger_level(log_level)

    if method not in METHOD_ACTION_MAP.keys():
        logger.error(f"Invalid method given: {method} is not accepted")
        raise typer.Exit(code=1)

    if Path(source_path).is_file():
        process_video(
            title=title, method=method, source_path=source_path, frames_per_second=fps,
        )
    elif Path(source_path).is_dir():
        process_dir(
            title=title, method=method, source_path=source_path, frames_per_second=fps,
        )
    logger.success("All done!")


def set_logger_level(log_level: str = "info") -> None:
    """
    Sets the logger level to the one provided at the commandline.

    Default loguru handler will have DEBUG level and ID 0.
    We need to first remove this default handler and add ours with the wanted level.

    Args:
        log_level: string, the default logging level to print out.

    Returns:
        Nothing, acts in place.
    """
    logger.remove(0)
    logger.add(sys.stderr, level=log_level.upper())


if __name__ == "__main__":
    app()
