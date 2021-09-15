"""
Created on 2019.08.13
:author: Felix Soubelet

Plotting functions for main script.
"""

import pathlib

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from loguru import logger

sns.set_palette("pastel")
sns.set_style("whitegrid")


def plot_shots_per_camera(subplot: matplotlib.axes.Axes, data: pd.DataFrame) -> None:
    """
	Barplot of the number of shots per camera, on the provided subplot. Acts in place.

    Args:
        subplot: the subplot matplotlib.axes.Axes on which to plot.
        data: the pandas DataFrame with your exif data.

    Returns:
        Nothing, plots in place.

    ??? warning "There is a danger here"
        Here is an explanation of the danger.
        Here is how to bypass it :)
    """
    logger.debug("Plotting shots per camera")
    sns.countplot(
        y="Camera", hue="Brand", data=data, ax=subplot, order=data.Camera.value_counts().index
    )
    subplot.set_title("Number of Shots per Camera Model", fontsize=25)
    subplot.tick_params(axis="both", which="major", labelsize=13)
    subplot.set_xlabel("Number of Shots", fontsize=20)
    subplot.set_ylabel("Camera Model", fontsize=20)
    subplot.legend(loc="lower right", fontsize=18, title_fontsize=22)


def plot_shots_per_fnumber(subplot: matplotlib.axes.Axes, data: pd.DataFrame) -> None:
    """
    Barplot of the number of shots per F number, on the provided subplot.

    Args:
        subplot: the subplot matplotlib.axes.Axes on which to plot.
        data: the pandas DataFrame with your exif data.

    Returns:
        Nothing, plots in place.
    """
    logger.debug("Plotting shots per aperture number")
    sns.countplot(x="F_Number", data=data, ax=subplot)
    subplot.set_title("Distribution of Apertures", fontsize=25)
    subplot.tick_params(axis="both", which="major", labelsize=13)
    subplot.tick_params(axis="x", rotation=70)
    subplot.set_xlabel("F Number", fontsize=20)
    subplot.set_ylabel("Number of Shots", fontsize=20)


def plot_shots_per_focal_length(subplot: matplotlib.axes.Axes, data: pd.DataFrame) -> None:
    """
    Barplot of the number of shots per focal length (FF equivalent), on the provided subplot.

    Args:
        subplot: the subplot matplotlib.axes.Axes on which to plot.
        data: the pandas DataFrame with your exif data.

    Returns:
        Nothing, plots in place.
    """
    logger.debug("Plotting shots per focal length")
    sns.countplot(
        x="Focal_Range",
        hue="Lens",
        data=data,
        ax=subplot,
        order=data.Focal_Range.value_counts().index,
    )
    subplot.set_title("Number of shots per Focal Length (FF equivalent)", fontsize=25)
    subplot.tick_params(axis="both", which="major", labelsize=13)
    subplot.set_xlabel("Focal Length", fontsize=20)
    subplot.set_ylabel("Number of Shots", fontsize=20)
    subplot.legend(loc="upper center", fontsize=15, title_fontsize=21)


def plot_shots_per_lens(subplot: matplotlib.axes.Axes, data: pd.DataFrame) -> None:
    """
    Barplot of the number of shots per lens used, on the provided subplot. Acts in place.

    Args:
        subplot: the subplot plt.axes on which to plot.
        data: the pandas DataFrame with your exif data.

    Returns:
        Nothing, plots in place.
    """
    logger.debug("Plotting shots per lens")
    sns.countplot(
        y="Lens", hue="Brand", data=data, ax=subplot, order=data.Lens.value_counts().index
    )
    subplot.set_title("Number of Shots per Lens Model", fontsize=25)
    subplot.tick_params(axis="both", which="major", labelsize=13)
    subplot.set_xlabel("Number of Shots", fontsize=20)
    subplot.set_ylabel("Lens Model", fontsize=20)
    subplot.legend(loc="lower right", fontsize=18, title_fontsize=25)


def plot_shots_per_shutter_speed(subplot: matplotlib.axes.Axes, data: pd.DataFrame) -> None:
    """
    Barplot of the number of shots per shutter speed, on the provided subplot. Acts in place.

    Args:
        subplot: the subplot plt.axes on which to plot.
        data: the pandas DataFrame with your exif data.

    Returns:
        Nothing, plots in place.
    """
    logger.debug("Plotting shots per shutter speed")
    sns.countplot(
        x="Shutter_Speed", data=data, ax=subplot, order=data.Shutter_Speed.value_counts().index
    )
    subplot.set_title("Number of Shots per Shutter Speed", fontsize=25)
    subplot.tick_params(axis="x", which="major", rotation=70)
    subplot.set_xlabel("Shutter Speed", fontsize=20)
    subplot.set_ylabel("Number of Shots", fontsize=20)


def plot_shots_per_year(subplot: matplotlib.axes.Axes, data: pd.DataFrame) -> None:
    """
    Barplot of the number of shots taken each year, on the provided subplot. Acts in place.

    Args:
        subplot: the subplot plt.axes on which to plot.
        data: the pandas DataFrame with your exif data.

    Returns:
        Nothing, plots in place.
    """
    logger.debug("Plotting shots per year")
    sns.countplot(
        y="Year", hue="Brand", data=data, ax=subplot, order=data.Year.value_counts().index
    )
    subplot.set_title("Number of Shots per Year", fontsize=25)
    subplot.tick_params(axis="both", which="major", labelsize=13)
    subplot.set_xlabel("Number of Shots", fontsize=20)
    subplot.set_ylabel("Year", fontsize=20)
    subplot.legend(loc="lower right", fontsize=18, title_fontsize=22)


def plot_shots_per_exposure_program_setting(
    subplot: matplotlib.axes.Axes, data: pd.DataFrame
) -> None:
    """
    Barplot of the number of shots per camera, on the provided subplot. Acts in place.

    Args:
        subplot: the subplot plt.axes on which to plot.
        data: the pandas DataFrame with your exif data.

    Returns:
        Nothing, plots in place.
    """
    logger.debug("Plotting shots per exposure program")
    sns.countplot(
        x="Exposure_Program",
        hue=None,
        palette="pastel",
        data=data,
        ax=subplot,
        order=data.Exposure_Program.value_counts().index,
    )
    subplot.set_title("Number of Shots per Exposure Program", fontsize=25)
    subplot.tick_params(axis="both", which="major", labelsize=13)
    subplot.set_xlabel("Exposure Program", fontsize=20)
    subplot.set_ylabel("Number of Shots", fontsize=20)


def plot_shots_per_flash_setting(subplot: matplotlib.axes.Axes, data: pd.DataFrame) -> None:
    """
    Barplot of the number of shots with or without flash, on the provided subplot. Acts in place.

    Args:
        subplot: the subplot plt.axes on which to plot.
        data: the pandas DataFrame with your exif data.

    Returns:
        Nothing, plots in place.
    """
    logger.debug("Plotting shots per flash setting")
    sns.countplot(
        x="Flash",
        hue=None,
        palette="pastel",
        data=data,
        ax=subplot,
        order=data.Flash.value_counts().index,
    )
    subplot.set_title("Number of Shots with and without Flash", fontsize=25)
    subplot.tick_params(axis="both", which="major", labelsize=13)
    subplot.set_xlabel("Flash Usage", fontsize=20)
    subplot.set_ylabel("Number of Shots", fontsize=20)


def plot_shots_per_metering_mode(subplot: matplotlib.axes.Axes, data: pd.DataFrame) -> None:
    """
    Barplot of the number of shots per metering mode, on the provided subplot. Acts in place.

    Args:
        subplot: the subplot plt.axes on which to plot.
        data: the pandas DataFrame with your exif data.

    Returns:
        Nothing, plots in place.
    """
    logger.debug("Plotting shots per metering mode")
    sns.countplot(
        x="Metering_Mode",
        hue=None,
        palette="pastel",
        data=data,
        ax=subplot,
        order=data.Metering_Mode.value_counts().index,
    )
    subplot.set_title("Number of Shots per Metering Mode", fontsize=25)
    subplot.tick_params(axis="both", which="major", labelsize=13)
    # subplot.tick_params(axis="x", rotation=45)
    subplot.set_xlabel("Metering Mode", fontsize=20)
    subplot.set_ylabel("Number of Shots", fontsize=20)


def plot_shots_per_white_balance_setting(subplot: matplotlib.axes.Axes, data: pd.DataFrame) -> None:
    """
    Barplot of the number of shots per white balance setting, on the provided subplot. Acts in
    place.

    Args:
        subplot: the subplot plt.axes on which to plot.
        data: the pandas DataFrame with your exif data.

    Returns:
        Nothing, plots in place.
    """
    logger.debug("Plotting shots per white balance setting")
    sns.countplot(
        y="White_Balance",
        hue=None,
        palette="pastel",
        data=data,
        ax=subplot,
        order=data.White_Balance.value_counts().index,
    )
    subplot.set_title("Number of Shots per White Balance Setting", fontsize=25)
    subplot.tick_params(axis="both", which="major", labelsize=13)
    subplot.set_xlabel("Number of Shots", fontsize=20)
    subplot.set_ylabel("White Balance", fontsize=20)


def plot_shots_per_exposure_compensation_setting(
    subplot: matplotlib.axes.Axes, data: pd.DataFrame
) -> None:
    """
    Barplot of the number of shots per Exposure Compensation setting, on the provided subplot.
    Acts in place.

    Args:
        subplot: the subplot plt.axes on which to plot.
        data: the pandas DataFrame with your exif data.

    Returns:
        Nothing, plots in place.
    """
    logger.debug("Plotting shots per exposure compensation setting")
    sns.countplot(
        x="Exposure_Compensation",
        hue=None,
        palette="pastel",
        data=data,
        ax=subplot,
        # order=data.Exposure_Compensation.value_counts().index,
    )
    subplot.set_title("Number of Shots per Exposure Compensation Setting", fontsize=25)
    subplot.tick_params(axis="both", which="major", labelsize=13)
    subplot.set_xlabel("Exposure Compensation", fontsize=20)
    subplot.set_ylabel("Number of Shots", fontsize=20)


def plot_shots_per_iso_setting(subplot: matplotlib.axes.Axes, data: pd.DataFrame) -> None:
    """
    Barplot of the number of shots per ISO setting, on the provided subplot. Acts in place.

    Args:
        subplot: the subplot plt.axes on which to plot.
        data: the pandas DataFrame with your exif data.

    Returns:
        Nothing, plots in place.
    """
    logger.debug("Plotting shots per ISO")
    sns.countplot(x="ISO", hue=None, data=data, ax=subplot)  # order=data.ISO.value_counts().index)
    subplot.set_title("Number of Shots per ISO Setting", fontsize=25)
    subplot.tick_params(axis="both", which="major", labelsize=13)
    subplot.set_xlabel("ISO Value", fontsize=20)
    subplot.set_ylabel("Number of Shots", fontsize=20)


def plot_insight(
    data: pd.DataFrame, output_directory: pathlib.Path, showfig: bool = False, savefig: bool = True
) -> None:
    """
    Combines all the different plots into subplots on two figure.

    Args:
        data: the pandas DataFrame with your exif data.
        output_directory: the folder in which to save the figures.
        showfig: if set to True, the figure will be shown. Defaults to False.
        savefig: if set to True, the figure will be saved. Defaults to True.

    Returns:
        Nothing, plots in place.
    """
    logger.info("Plotting first insights figure")

    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(20, 22))
    fig.suptitle("Your Photography Habits - Part 1", fontsize=35)
    plot_shots_per_year(axes[0, 0], data)
    plot_shots_per_camera(axes[0, 1], data)
    plot_shots_per_lens(axes[1, 0], data)
    plot_shots_per_focal_length(axes[1, 1], data)
    plot_shots_per_fnumber(axes[2, 0], data)
    plot_shots_per_shutter_speed(axes[2, 1], data)
    fig.tight_layout()
    fig.subplots_adjust(top=0.93)

    if showfig:
        logger.debug("Showing first insight figure.")
        plt.show()

    if savefig:
        logger.debug(f"Saving first insights figure as {output_directory}/insight_1.png")
        plt.savefig(f"{output_directory}/insight_1.jpg", format="jpg", dpi=500)
        logger.success(f"Saved as {output_directory}/insight_1.jpg")

    logger.info("Plotting second insights figure")

    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(20, 22))
    fig.suptitle("Your Photography Habits - Part 2", fontsize=35)
    plot_shots_per_exposure_program_setting(axes[0, 0], data)
    plot_shots_per_flash_setting(axes[0, 1], data)
    plot_shots_per_metering_mode(axes[1, 0], data)
    plot_shots_per_white_balance_setting(axes[1, 1], data)
    plot_shots_per_exposure_compensation_setting(axes[2, 0], data)
    plot_shots_per_iso_setting(axes[2, 1], data)
    fig.tight_layout()
    fig.subplots_adjust(top=0.93)

    if showfig:
        logger.debug("Showing second insight figure.")
        plt.show()

    if savefig:
        logger.debug(f"Saving second insights figure as {output_directory}/insight_2.png")
        plt.savefig(f"{output_directory}/insight_2.jpg", format="jpg", dpi=500)
        logger.success(f"Saved as {output_directory}/insight_2.jpg")


# ================================================================================================ #


if __name__ == "__main__":
    raise NotImplementedError("This module is meant too be imported")
