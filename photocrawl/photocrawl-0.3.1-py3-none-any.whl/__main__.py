"""
Running directly from python module.
"""

import pathlib

import typer

from photocrawl.photocrawl import PhotoCrawler
from photocrawl.plotting_functions import plot_insight
from photocrawl.utils import set_logger_level, setup_output_directory

app = typer.Typer()


@app.command()
def crawl(
    images: str = typer.Argument(
        None, help="Location, relative or absolute, of the images directory you wish to crawl.",
    ),
    output_dir: str = typer.Option(
        "outputs", help="Location, either relative or absolute, of the output directory."
    ),
    show_figures: bool = typer.Option(
        False, help="Whether or not to show figures when plotting insights."
    ),
    save_figures: bool = typer.Option(
        False, help="Whether or not to save figures when plotting insights."
    ),
    log_level: str = typer.Option(
        "info",
        help="The base console logging level. Can be 'debug', 'info', 'warning' and 'error'.",
    ),
) -> None:
    """
    Crawl and ensemble of pictures to run analysis of their metadata and get insight on one's use of
    equipment and settings in their practice of photography.
    """
    set_logger_level(log_level)

    output_directory: pathlib.Path = setup_output_directory(output_dir)
    files_location = pathlib.Path(images)

    crawler = PhotoCrawler(files_location)
    exif_data_df: pd.DataFrame = crawler.process_files()
    exif_data_df = crawler.refactor_exif_data(exif_data_df)

    plot_insight(
        data=exif_data_df,
        output_directory=output_directory,
        showfig=show_figures,
        savefig=save_figures,
    )


if __name__ == "__main__":
    app()
