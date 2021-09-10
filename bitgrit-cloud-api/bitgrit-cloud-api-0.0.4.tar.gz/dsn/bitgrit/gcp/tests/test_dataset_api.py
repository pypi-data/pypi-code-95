from dsn.bitgrit.gcp.dataset_api import DatasetAPI
from dsn.bitgrit.datasets.dataset import Dataset
import google
import asyncio
from unittest.mock import patch, mock_open
import unittest
import os

TEST_BUCKET = "dataset-images"


class TestDatasetAPI(unittest.TestCase):

    def setUp(self):
        self.bucket_name = TEST_BUCKET
        self.dataset_api = DatasetAPI(
            self.bucket_name
        )
        self.fake_dataset = os.environ['PWD'] + \
            "/dsn/bitgrit/gcp/tests/assets/testfile.zip"

    @patch.object(google.cloud.storage.Bucket, 'blob', autospec=True)
    @patch('google.cloud.storage.Blob', autospec=True)
    def test_create_directory(self, mock_blob, mock_method_blob):
        mock_method_blob.return_value = mock_blob

        loop = asyncio.get_event_loop()
        ret = loop.run_until_complete(
            self.dataset_api.create_directory("useless name"))

        mock_method_blob.assert_called_once()
        mock_blob.upload_from_string.assert_called_once()
        self.assertTrue(ret)

    @patch.object(google.cloud.storage.Bucket, 'blob', autospec=True)
    @patch('google.cloud.storage.Blob', autospec=True)
    def test_upload_file(self, mock_blob, mock_method_blob):
        mock_method_blob.return_value = mock_blob

        loop = asyncio.get_event_loop()
        ret = loop.run_until_complete(self.dataset_api.upload_file(
            self.fake_dataset, 'dest'))

        mock_method_blob.assert_called_once()
        mock_blob.upload_from_filename.assert_called_once()
        self.assertTrue(ret)

    @patch.object(google.cloud.storage.Bucket, 'blob', autospec=True)
    @patch('google.cloud.storage.Blob', autospec=True)
    def test_download_file(self, mock_blob, mock_method_blob):
        mock_method_blob.return_value = mock_blob

        loop = asyncio.get_event_loop()
        ret = loop.run_until_complete(
            self.dataset_api.download_file("fake name",
                                           "fake name"))
        mock_method_blob.assert_called_once()
        mock_blob.download_to_filename.assert_called_once()
        self.assertTrue(ret)

    @patch.object(google.cloud.storage.Bucket, 'get_blob', autospec=True)
    @patch('google.cloud.storage.Blob', autospec=True)
    def test_set_metadata(self, mock_blob, mock_method_get_blob):
        mock_method_get_blob.return_value = mock_blob

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.dataset_api.set_metadata(
            "fake dataset name",
            {"fake-key": "fake-value"}))

        mock_method_get_blob.assert_called_once()
        mock_blob.patch.assert_called_once()
        assert mock_blob.metadata["fake-key"] == "fake-value"

    @patch.object(google.cloud.storage.Bucket, 'get_blob', autospec=True)
    @patch('google.cloud.storage.Blob', autospec=True)
    def test_get_metadata(self, mock_blob, mock_method_get_blob):
        mock_method_get_blob.return_value = mock_blob
        mock_blob.metadata = {"fake-key": "fake-value"}

        loop = asyncio.get_event_loop()
        ret = loop.run_until_complete(
            self.dataset_api.get_metadata("dataset name", "fake-key"))

        mock_method_get_blob.assert_called_once()
        assert ret == "fake-value"

    @patch('google.cloud.storage.Bucket', autospec=True)
    @patch.object(google.cloud.storage.Bucket, 'get_blob', autospec=True)
    @patch('google.cloud.storage.Blob', autospec=True)
    def test_get_complete_metadata(self, mock_blob, mock_method_get_blob
                                   , mock_bucket):
        mock_method_get_blob.return_value = mock_blob
        mock_blob.name = "fake-blob"
        mock_blob.bucket = mock_bucket
        mock_bucket.name = "fake-bucket"

        loop = asyncio.get_event_loop()
        ret = loop.run_until_complete(
            self.dataset_api.get_complete_metadata("dataset name"))

        mock_method_get_blob.assert_called_once()
        assert ret["dataset"] == "fake-blob"
        assert ret["bucket"] == "fake-bucket"

    @patch.object(google.cloud.storage.Bucket, 'list_blobs', autospec=True)
    @patch('google.cloud.storage.Blob', autospec=True)
    def test_list_datasets(self, mock_blob, mock_method_list_blobs):
        mock_method_list_blobs.return_value = iter([mock_blob])
        mock_blob.name = "fake-blob"

        loop = asyncio.get_event_loop()
        ret = loop.run_until_complete(self.dataset_api.list_datasets())

        mock_method_list_blobs.assert_called_once()
        self.assertIsInstance(ret[0], Dataset)

    @patch.object(google.cloud.storage.Bucket, 'blob', autospec=True)
    @patch('google.cloud.storage.Blob', autospec=True)
    def test_delete_file(self, mock_blob, mock_method_blob):
        mock_method_blob.return_value = mock_blob

        loop = asyncio.get_event_loop()
        ret = loop.run_until_complete(
            self.dataset_api.delete_file("dataset name"))

        mock_method_blob.assert_called_once()
        mock_blob.delete.assert_called_once()
        self.assertTrue(ret)

    @patch.object(google.cloud.storage.Bucket, 'list_blobs', autospec=True)
    @patch('google.cloud.storage.Blob', autospec=True)
    def test_get_metadata_to_datasets_hash(self, mock_blob,
                                           mock_method_list_blobs):
        mock_method_list_blobs.return_value = iter([mock_blob])
        mock_blob.metadata = {"fake-key": "fake-value"}
        mock_blob.name = "fake-blob"

        loop = asyncio.get_event_loop()
        ret = loop.run_until_complete(
            self.dataset_api.get_metadata_to_datasets_hash("fake-key"))

        mock_method_list_blobs.assert_called_once()
        self.assertIsInstance(ret["fake-value"][0], Dataset)


if __name__ == '__main__':
    unittest.main()
