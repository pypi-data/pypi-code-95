from typing import Tuple
import os
from downloaders import BaseDownloader
import pandas as pd


def load_aggregated_conservation_scores(
    assembly: str = "hg38",
    dataset: str = "fantom",
    region: str = "promoters",
    metric: str = "mean",
    window_size: int = 256,
    imputed: bool = True,
    root: str = "datasets",
    verbose: int = 2
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return aggregated conservation scores data for given parameters.

    Parameters
    ----------------------------------------
    assembly: str = "hg38",
        The genomic assembly of the data to be retrieved.
    dataset: str = "fantom",
        Dataset to consider. By default fantom.
        Currently available datasets are
        listed in the repository README file.
    region: str = "promoters",
        Region to consider. By default promoters.
        Currently available region are
        listed in the repository README file.
    metric: str = "mean",
        The metric to load.
    window_size: int = 256,
        Window size to consider. By default 256.
        Currently available window sizes are
        listed in the repository README file.
    imputed: bool = True,
        Whether to load the version of the dataset that has
        already been imputed.
    root: str = "datasets"
        Where to store the downloaded data.
    verbose: int = 2,
        Verbosity level.

    Returns
    ----------------------------------------
    Return tuple with input and output DataFrames.
    """

    repository = "https://github.com/LucaCappelletti94/conservation_scores_dataset/blob/main/"
    get_parameter = "?raw=true"
    data_path_placeholder = "{{root}}/aggregated_{imputed}conservation_scores/{assembly}/{dataset}/{region}/{window_size}.tsv.xz".format(
        imputed="imputed_" if imputed else "",
        assembly=assembly,
        dataset=dataset,
        window_size=window_size,
        region=region,
    )

    data_path = data_path_placeholder.format(root=root)
    downloader = BaseDownloader(
        target_directory=root,
        verbose=verbose,
        auto_extract=False
    )

    downloader.download(
        urls=data_path_placeholder.format(root=repository)+get_parameter,
        paths=data_path
    )

    X = pd.read_csv(
        data_path,
        index_col=[0, 1, 2, 3, 4],
        header=[0, 1],
        low_memory=False,
        sep="\t"
    )

    X = X[[
        col
        for col in X.columns
        if metric in col
    ]]

    X = X.droplevel(1, axis=1)

    return X
