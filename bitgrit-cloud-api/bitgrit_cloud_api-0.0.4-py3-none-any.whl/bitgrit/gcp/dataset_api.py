from dsn.bitgrit.gcp import storage_client
from dsn.bitgrit.datasets.helper import valid_filetype


class DatasetAPI:

    def __init__(self, bucket_name):
        self._bucket_name = bucket_name
        self._storage_client = storage_client
        self._bucket = None
        self._load_bucket()

    @property
    def bucket_name(self):
        return self._bucket_name

    @bucket_name.setter
    def bucket_name(self, bucket_name):
        self._bucket_name = bucket_name
        self._load_bucket()

    def _load_bucket(self):
        try:
            self._bucket = self._storage_client.get_bucket(self._bucket_name)
        except Exception as e:
            raise Exception(e)

    def _convert_blob_to_dataset(self, blob):
        from dsn.bitgrit.datasets.dataset import Dataset
        return Dataset(self.bucket_name, blob.name)

    async def list_datasets(self, prefix='', delimiter=None):
        """Lists all the datasets in the bucket."""
        try:
            if prefix:
                blob_list = self._bucket.list_blobs(
                    prefix=prefix,
                    delimiter=delimiter
                )
                return list(map(self._convert_blob_to_dataset, blob_list))
            blob_list = list(self._bucket.list_blobs())
            return list(map(self._convert_blob_to_dataset, blob_list))
        except Exception as e:
            raise Exception(e)

    async def create_directory(self, dir_name):
        """create directory in the bucket.
        Parameter :
        dir_name : name of directory to be created.
        """
        try:
            self._bucket.blob(dir_name + '/').upload_from_string(
                '', content_type='application/x-www-form-urlencoded;' +
                                 'charset=UTF-8'
            )
            return True
        except Exception as e:
            raise Exception(e)

    async def delete_directory(self, dir_name):
        try:
            self._bucket.blob(dir_name + '/').delete()
            return True
        except Exception as e:
            raise Exception(e)

    async def upload_file(self, source_file_name, destination_file_name):
        """Uploads dataset to the bucket.
        Parameters :
        1. source_file_name : Source file name with full path (Local)
        2. destination_file_name : i.e. filename or dirname/filename
        """
        try:
            if valid_filetype(source_file_name):
                self._bucket.blob(
                    destination_file_name
                ).upload_from_filename(source_file_name)
                return True
            else:
                raise TypeError('Invalid File type.' +
                                'We only support zip file format currently')
        except Exception as e:
            raise Exception(e)

    async def download_file(self, file_name, destination_file_name=''):
        """Download the dataset file."""
        try:
            if destination_file_name:
                self._bucket.blob(file_name).download_to_filename(
                    destination_file_name)
            else:
                self._bucket.blob(file_name).download_to_filename(
                    file_name)
            return True
        except Exception as e:
            raise Exception(e)

    async def delete_file(self, file_name):
        try:
            self._bucket.blob(file_name).delete()
            return True
        except Exception as e:
            raise Exception(e)

    async def set_metadata(self, file_name, values):
        """Add metadata to dataset file."""
        try:
            dataset = self._bucket.get_blob(file_name)
            dataset.metadata = values
            dataset.patch()
            return True
        except Exception as e:
            raise Exception(e)

    async def get_metadata(self, file_name, key_name):
        """get metadata value of dataset file by key."""
        try:
            dataset = self._bucket.get_blob(file_name)
            mdata = dataset.metadata
            return mdata[key_name]
        except Exception as e:
            raise Exception(e)

    async def get_complete_metadata(self, file_name):
        """Get complete metadata of a dataset."""
        try:
            dataset = self._bucket.get_blob(file_name)

            mdata = {
                'dataset': dataset.name,
                'bucket': dataset.bucket.name,
                'storage_class': dataset.storage_class,
                'id': dataset.id,
                'size': dataset.size,
                'updated_at': dataset.updated,
                'generation': dataset.generation,
                'metageneration': dataset.metageneration,
                'etag': dataset.etag,
                'owner': dataset.owner,
                'component_count': dataset.component_count,
                'crc32c': dataset.crc32c,
                'md5_hash': dataset.md5_hash,
                'cache_control': dataset.cache_control,
                'content_type': dataset.content_type,
                'content_disposition': dataset.content_disposition,
                'content_encoding': dataset.content_encoding,
                'content_language': dataset.content_language,
                'public_url': dataset.public_url,
                'metadata': dataset.metadata,
                'iam': dataset.get_iam_policy(),
                'temporary_hold': 'enabled' if dataset.temporary_hold
                else 'disabled',
                'event_based_hold': 'enabled' if dataset.event_based_hold
                else 'disabled'
            }

            if dataset.retention_expiration_time:
                mdata['retention_expiration_time'] \
                    = dataset.retention_expiration_time

            return mdata
        except Exception as e:
            raise Exception(e)

    async def get_metadata_to_datasets_hash(self, key):
        """get key:[datasets] hash"""
        try:
            blobs = self._bucket.list_blobs()
            reverse_hash = {}
            for blob in blobs:
                mdata = blob.metadata
                if mdata and key in mdata:
                    val = mdata[key]
                    if key in mdata:
                        if val in reverse_hash:
                            reverse_hash[val] += \
                                [self._convert_blob_to_dataset(blob)]
                        else:
                            reverse_hash[val] = \
                                [self._convert_blob_to_dataset(blob)]
            return reverse_hash
        except Exception as e:
            raise Exception(e)
