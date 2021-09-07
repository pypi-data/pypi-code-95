"""Module for retrieval of entire batches"""
from typing import List, Union
from tqdm.auto import tqdm
from epigenomic_dataset import load_epigenomes
import compress_json
import os
from .extract import extract


def retrieve_all(
    assembly: str = "hg38",
    datasets: Union[str, List[str]] = "auto",
    regions: Union[str, List[str]] = "auto",
    window_sizes: Union[str, int, List[int]] = "auto",
    clear_download: bool = False,
    cache_directory: str = "conservation_scores"
):
    """Download and mines all data relative to conservation scores for HG38.

    Parameters
    ---------------------------
    assembly: str = "hg38",
        The assembly to retrieve.
    datasets: Union[str, List[str]] = "auto",
        The dataset to retrieve, currently FANTOM5 and ROADMAP are supported.
        The default value, "auto", means that all the currently available datasets will be retrieved.
    regions: Union[str, List[str]] = "auto",
        The region to retrieve the data for.
        It can either be "promoters" or "enhancers".
        The default value, "auto", means that all the currently available regions will be retrieved.
    window_sizes: Union[str, int, List[int]] = "auto",
        The window size to mine.
        The default value, "auto", means that all the currently available window sizes will be retrieved.
    clear_download: bool = False,
        Whether to clear the data once downloaded.
    """
    # Normalize the input data
    if datasets == "auto":
        datasets = ["fantom", "roadmap"]
    if regions == "auto":
        regions = ["enhancers", "promoters"]
    if window_sizes == "auto":
        window_sizes = [64, 128, 256, 512, 1024]
    if isinstance(datasets, str):
        datasets = [datasets]
    if isinstance(regions, str):
        regions = [regions]
    if isinstance(window_sizes, int):
        window_sizes = [window_sizes]
    for dataset in tqdm(
        datasets,
        desc="Retrieve different datasets",
        leave=False,
        disable=len(datasets) == 1
    ):
        for region in tqdm(
            regions,
            desc="Retrieve different regions",
            leave=False,
            disable=len(regions) == 1
        ):
            for window_size in tqdm(
                window_sizes,
                desc="Retrieve different window sizes",
                leave=False,
                disable=len(window_sizes) == 1
            ):
                # Retrieving the epigenomic data
                # We retrieve the labels from here and not directly from crr labels
                # only because the labels are cached in load epigenomes and they
                # do not require further processing.
                _, y = load_epigenomes(
                    assembly=assembly,
                    dataset=dataset,
                    region=region,
                    window_size=window_size,
                )

                bed_path = os.path.join(
                    cache_directory,
                    assembly,
                    dataset,
                    region,
                    "{}.bed".format(window_size)
                )

                os.makedirs(os.path.dirname(bed_path), exist_ok=True)

                bed = y.reset_index()[y.index.names]
                bed.to_csv(bed_path, sep="\t", header=False, index=False)

                urls = compress_json.local_load("urls.json")[assembly]
                for type_name, data_urls in tqdm(
                    list(urls.items()),
                    desc="Retrieve all types of conservation data",
                    leave=False
                ):
                    for specific_type, url in tqdm(
                        list(data_urls.items()),
                        desc="Retrieve data of type {}".format(type_name),
                        leave=False
                    ):
                        bigwig_path = os.path.join(
                            cache_directory,
                            assembly,
                            type_name,
                            "{}.bw".format(specific_type),
                        )

                        target_path = os.path.join(
                            cache_directory,
                            assembly,
                            type_name,
                            specific_type,
                            dataset,
                            region,
                            "{}.tsv".format(window_size),
                        )

                        os.makedirs(os.path.dirname(
                            bigwig_path), exist_ok=True)
                        os.makedirs(os.path.dirname(
                            target_path), exist_ok=True)

                        extract(
                            bed_path,
                            bigwig_path,
                            target_path,
                            url,
                            clear_download=clear_download
                        )
