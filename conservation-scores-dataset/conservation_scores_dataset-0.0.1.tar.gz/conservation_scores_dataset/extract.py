import os
from downloaders import BaseDownloader
import pandas as pd
from pybwtool import extract as extract_bigwig


def extract(
    bed_path: str,
    bigwig_path: str,
    target_path: str,
    url: str,
    clear_download: bool
):
    """Extract provided BED file regions from given bigwig.

    Parameters
    ---------------------
    bed_path: str,
        The path to the provided BED file.
    bigwig_path: str,
        Path where to download the requested bigwig.
    target_path: str,
        Path where to store the extracted regions.
    url: str,
        URL from where to download the bigwig.
    clear_download: bool,
        Whether to clear the downloaded file.
    """
    # Download file if it does not already exist
    if not os.path.exists(bigwig_path) and not os.path.exists(target_path):
        BaseDownloader().download(
            url, bigwig_path
        )

    # Extract the features
    extract_bigwig(
        bed_path=bed_path,
        bigwig_path=bigwig_path,
        target=target_path
    )

    # Reloading file and storing it as compressed file
    pd.read_csv(target_path, sep="\t").to_csv(
        "{}.xz".format(target_path),
        index=False
    )

    # Removing non compressed version of the file
    os.remove(target_path)

    # Remove the bigwig file if required
    if clear_download:
        os.remove(bigwig_path)
