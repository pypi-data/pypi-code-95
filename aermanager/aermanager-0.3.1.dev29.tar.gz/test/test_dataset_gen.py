import numpy as np
from aermanager.dataset_generator import (
    dataset_content_generator,
    save_to_dataset,
    _get_lists_from_subfolders,
    gen_dataset_from_csv,
)
from pathlib import Path
import shutil

HERE = Path(__file__).parent


def test_save_to_folder():
    sliced_xytp, frames, bins = dataset_content_generator(
        HERE / "data" / "class2" / "data_sample.aedat4",
        time_window=50000
    )
    save_to_dataset(sliced_xytp, frames, np.arange(len(sliced_xytp)),
                    bins=(0, 0),  # fake data
                    destination_path=HERE / "dataset")
    assert (HERE / "dataset").glob("data_sample_*/0.h5")
    shutil.rmtree(HERE / "dataset")


def test_lists_from_subfolders():
    folder = HERE / "data"
    files, labels = _get_lists_from_subfolders(folder)
    assert files == [folder / "class1" / "test.aedat4",
                     folder / "class2" / "data_sample.aedat4"]
    assert labels == ["class1", "class2"]


def test_save_from_csv():
    gen_dataset_from_csv(
        csv_file=HERE / "data" / "list.csv",
        destination_path=HERE / "dataset",
        source_folder=HERE / "data",
        time_window=50000,
    )
    assert (HERE / "dataset").glob("data_sample_*/0.h5")
    assert (HERE / "dataset").glob("test_*/0.h5")
    shutil.rmtree(HERE / "dataset")
