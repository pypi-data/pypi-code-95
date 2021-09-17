import shutil
from test.conftest import USE_MOCK
from test.util import random_string

import pytest

import savvihub
from savvihub.util.exception import SavvihubApiException


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestDataset:
    dataset_name = random_string()

    @classmethod
    def teardown_class(cls):
        shutil.rmtree("test/fixture/tmp/", ignore_errors=True)

    @pytest.mark.order(index=1)
    def test_create_dataset(self):
        savvihub.create_dataset(
            dataset_name=self.dataset_name,
            description=random_string(),
        )
        # TODO: test s3 and gs datasets

    @pytest.mark.order(index=2)
    def test_upload_dataset_volume_file(self):
        savvihub.upload_dataset_volume_file(
            self.dataset_name, "test/fixture/file1.txt", "file1.txt"
        )
        savvihub.upload_dataset_volume_file(
            self.dataset_name, "test/fixture/folder1", "folder1", recursive=True
        )

    def test_read_dataset(self):
        savvihub.read_dataset(self.dataset_name)

    def test_list_datasets(self):
        savvihub.list_datasets()

    def test_list_dataset_volume_files(self):
        savvihub.list_dataset_volume_files(self.dataset_name)

    def test_download_dataset_volume_file(self):
        savvihub.download_dataset_volume_file(
            self.dataset_name, "file1.txt", "test/fixture/tmp/file2.txt"
        )
        savvihub.download_dataset_volume_file(
            self.dataset_name, "folder1", "test/fixture/tmp/folder1", recursive=True
        )

    def test_copy_dataset_volume_file(self):
        savvihub.copy_dataset_volume_file(
            self.dataset_name, "file1.txt", "file1_copy.txt"
        )
        savvihub.copy_dataset_volume_file(
            self.dataset_name, "folder1", "folder1_copy", recursive=True
        )
        with pytest.raises(SavvihubApiException):
            savvihub.copy_dataset_volume_file(
                self.dataset_name, "folder1", "folder1_copy"
            )

    @pytest.mark.order(index=-1)
    def test_delete_dataset_volume_file(self):
        savvihub.delete_dataset_volume_file(self.dataset_name, "file1.txt")
        savvihub.delete_dataset_volume_file(
            self.dataset_name, "folder1", recursive=True
        )
        with pytest.raises(SavvihubApiException):
            savvihub.delete_dataset_volume_file(self.dataset_name, "folder1")
