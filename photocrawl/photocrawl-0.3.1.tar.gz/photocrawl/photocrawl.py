"""
Created on 2019.08.15
:author: Felix Soubelet

A simply script to run analysis and get insight on my use of equipment and settings in my
practice of photography.
"""

import pathlib
import shlex
from multiprocessing import Pool, cpu_count
from typing import Dict, List

import pandas as pd
import pendulum
import pyexifinfo as pyexif
from loguru import logger

from photocrawl.utils import figure_focal_range, timeit


class PhotoCrawler:
    """
    Class to handle the crawling and processing of different files.
    """

    __slots__ = {
        "top_level_location": "PosixPath object to the directory to crawl for images",
        "categorical_columns": "List of EXIF properties to treat as categoories",
        "columns_renaming_dict": "Dictionary of EXIF properties to rename",
        "interesting_features": "List of EXIF properties to look for and treat",
        "lens_tags_mapping": "Dictionary of EXIF lens tags to rename",
        "metering_modes_mapping": "Dictionary of EXIF metering modes to rename",
        "raw_formats": "Dictionary of RAW file formats and their descriptions",
    }

    def __init__(self, directory_to_crawl: pathlib.Path):
        self.top_level_location: pathlib.Path = directory_to_crawl
        self.categorical_columns: List[str] = [
            "Exposure_Compensation",
            "Exposure_Program",
            "Flash",
            "Lens_Brand",
            "Lens",
            "Brand",
            "Metering_Mode",
            "Camera",
            "Shutter_Speed",
            "White_Balance",
            "Focal_Range",
        ]
        self.columns_renaming_dict: Dict[str, str] = {
            "ExposureCompensation": "Exposure_Compensation",
            "ExposureProgram": "Exposure_Program",
            "FNumber": "F_Number",
            "FocalLength": "Focal_Length",
            "FocalLengthIn35mmFormat": "Focal_Length",
            "LensMake": "Lens_Brand",
            "LensModel": "Lens",
            "Make": "Brand",
            "MeteringMode": "Metering_Mode",
            "Model": "Camera",
            "ShutterSpeedValue": "Shutter_Speed",
            "WhiteBalance": "White_Balance",
        }
        self.interesting_features: List[str] = [
            "DateTimeOriginal",
            "ExposureCompensation",
            "ExposureProgram",
            "FNumber",
            "Flash",
            "FocalLength",
            "FocalLengthIn35mmFormat",
            "ISO",
            "LensMake",
            "LensModel",
            "Make",
            "MeteringMode",
            "Model",
            "ShutterSpeedValue",
            "WhiteBalance",
        ]
        self.lens_tags_mapping: Dict[str, str] = {
            "XF10-24mmF4 R OIS": "XF 10-24mm f/4 R",
            "XF18-135mmF3.5-5.6R LM IOS WR": "XF 18-135mm f/3.5-5.6 R LM OIS WR",
            "XF18-55mmF2.8-4 R LM OIS": "XF 18-55mm f/2.8-4 R LM OIS",
            "XF23mmF1.4 R": "XF 23mm f/1.4 R",
            "XF50-140mmF2.8 R LM OIS WR": "XF 50-140mm f/2.8 R LM OIS WR",
            "XF50-140mmF2.8 R LM OIS WR + 1.4x": "XF 50-140mm f/2.8 R LM OIS WR + 1.4x",
            "XF55-200mmF3.5-4.8 R LM OIS": "XF 55-200mm f/3.5-4.8 R LM OIS",
            "XF56mmF1.2 R APD": "XF 56mm f/1.2 R APD",
        }
        self.metering_modes_mapping: Dict[str, str] = {
            "Center-weighted average": "Center Weighted",
            "Multi-segment": "Multi Segment",
        }
        self.raw_formats: Dict[str, str] = {
            "JPG": "The classic jpg file format",
            "JPEG": "Also the jpg file format",
            "3FR": "Hasselblad 3F RAW Image",
            "ARI": "ARRIRAW Image",
            "ARW": "Sony Digital Camera Image",
            "BAY": "Casio RAW Image",
            "CR2": "Canon Raw Image File",
            "CR3": "Canon Raw 3 Image File",
            "CRW": "Canon Raw CIFF Image File",
            "CS1": "CaptureShop 1-shot Raw Image",
            "CXI": "FMAT RAW Image",
            "DCR": "Kodak RAW Image File",
            "DNG": "Digital Negative Image File",
            "EIP": "Enhanced Image Package File",
            "ERF": "Epson RAW File",
            "FFF": "Hasselblad RAW Image",
            "IIQ": "Phase One RAW Image",
            "J6I": "Ricoh Camera Image File",
            "K25": "Kodak K25 Image",
            "KDC": "Kodak Photo-Enhancer File",
            "MEF": "Mamiya RAW Image",
            "MFW": "Mamiya Camera Raw File",
            "MOS": "Leaf Camera RAW File",
            "MRW": "Minolta Raw Image File",
            "NEF": "Nikon Electronic Format RAW Image",
            "NRW": "Nikon Raw Image File",
            "ORF": "Olympus RAW File",
            "PEF": "Pentax Electronic File",
            "RAF": "Fuji RAW Image File",
            "RAW": "Raw Image Data File",
            "RW2": "Panasonic RAW Image",
            "RWL": "Leica RAW Image",
            "RWZ": "Rawzor Compressed Image",
            "SR2": "Sony RAW Image",
            "SRF": "Sony RAW Image",
            "SRW": "Samsung RAW Image",
            "X3F": "SIGMA X3F Camera RAW File",
        }
        logger.debug("PhotoCrawler instantiation successful")

    def get_exif(self, photo_file: str) -> Dict[str, str]:
        """
        Returns a dictionary with interesting features from image EXIF.

        Args:
            photo_file: A `pathlib.Path` object with the bsolute path to the file location.

        Returns:
            A dictionary with the exif fields and value for the specific file.
        """
        logger.trace(f"Extracting exif for file {photo_file}")
        return {
            key[5:]: value
            for key, value in pyexif.get_json(photo_file)[0].items()
            if key[5:] in self.interesting_features
        }

    def crawl_files(self) -> List[str]:
        """
        Recursively go over relevant files in the `top_level_localtion` directory and
        sub-directories, and return a list of PosixPath to each relevant file.

        Returns:
            A list.
        """
        logger.debug(f"Crawling '{self.top_level_location.absolute()}' for relevant files")
        crawled_images: List[str] = []
        with timeit(
            lambda spanned: logger.info(
                f"Crawled and found {len(crawled_images)} relevant files in {spanned:.4f} seconds"
            )
        ):
            for extension in self.raw_formats.keys():
                crawled_images.extend(self.top_level_location.rglob(f"*.{extension}"))
                crawled_images.extend(self.top_level_location.rglob(f"*.{extension.lower()}"))
            crawled_images = sorted(str(result) for result in crawled_images)
        return crawled_images

    def process_files(self) -> pd.DataFrame:
        """
        Go over the crawled files in the `top_level_localtion` directory and sub-directories,
        and organize their exif data in a `pandas.DataFrame`.

        Returns:
            A `pandas.DataFrame` with exif information for each file. Each file's information is
            a row, and each column corresponds to an exif data field.
        """
        logger.debug("Gathering exif metadata from crawled files")
        crawled_images: List[str] = self.crawl_files()

        with timeit(
            lambda spanned: logger.info(
                f"Gathered metadata of {len(crawled_images)} files in {spanned:.4f} seconds"
            )
        ):
            with Pool(cpu_count()) as pool:
                metadata = pd.DataFrame(list(pool.imap_unordered(self.get_exif, crawled_images)))
        return metadata

    @logger.catch()
    def refactor_exif_data(self, crawled_exif: pd.DataFrame) -> pd.DataFrame:
        """
        Refactor the `pandas.Dataframe` with crawled exif data by improving labels and
        categorizing some content from original, in a convenient way.

        Returns:
            A new `pandas.DataFrame` with refactored data.
        """
        logger.debug("Refactoring gathered exif metadata for plotting")
        with timeit(lambda spanned: logger.info(f"Refactorred metadata in {spanned:.4f} seconds")):
            working_df: pd.DataFrame = crawled_exif.copy(deep=True)

            logger.debug("Renaming exif fields")
            working_df.rename(self.columns_renaming_dict, axis="columns", inplace=True)
            working_df.dropna(inplace=True)

            logger.debug("Refactoring shots dates")
            working_df["Year"] = working_df["DateTimeOriginal"].apply(
                lambda x: pendulum.parse(x).year
            )
            working_df["Month"] = working_df["DateTimeOriginal"].apply(
                lambda x: pendulum.parse(x).month
            )
            working_df["Day"] = working_df["DateTimeOriginal"].apply(
                lambda x: pendulum.parse(x).day
            )

            logger.debug("Extrapolating focal ranges")
            working_df["Focal_Length"] = working_df["Focal_Length"].apply(
                lambda x: float(shlex.split(x)[0])
            )
            working_df["Focal_Range"] = working_df["Focal_Length"].apply(figure_focal_range)

            logger.debug("Making data categorical")
            for column in self.categorical_columns:
                if column in working_df.columns.to_numpy():
                    working_df[column] = working_df[column].astype("category")

            # Does mapping, falls back to original names for values absent in the mapping dictionary
            logger.debug("Refactoring metering mode names")
            working_df["Metering_Mode"] = (
                working_df["Metering_Mode"]
                .map(self.metering_modes_mapping)
                .fillna(working_df["Metering_Mode"])
            )

            # Does mapping, falls back to original names for values absent in the mapping dictionary
            logger.debug("Refactoring lens names, might not be exhaustive")
            working_df["Lens"] = working_df["Lens"].cat.remove_unused_categories()
            working_df["Lens"] = (
                working_df["Lens"].map(self.lens_tags_mapping).fillna(working_df["Lens"])
            )
        return working_df.dropna()
