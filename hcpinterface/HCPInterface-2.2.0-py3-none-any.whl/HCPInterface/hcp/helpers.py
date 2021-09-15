import os
import hashlib

from HCPInterface.hcp.config import get_config

config = get_config()


def calculate_etag(local_path):
    file_size = os.stat(local_path).st_size
    size_threshold = int(config.get('hcp', 'size_threshold'))

    chunk_size = int(config.get('hcp', 'chunk_size'))
    if file_size > size_threshold:

        chunk_hashes = []
        with open(local_path, 'rb') as fp:
            while True:
                data_chunk = fp.read(chunk_size)
                if not data_chunk:
                    break

                chunk_hashes.append(hashlib.sha256(data_chunk))

        binary_digests = b''.join(chunk_hash.digest() for chunk_hash in chunk_hashes)
        binary_hash = hashlib.sha256(binary_digests).hexdigest()
        return f'"{binary_hash}-{len(chunk_hashes)}"'

    else:
        file_hash = hashlib.md5()
        with open(local_path, 'rb') as fp:
            while True:
                data_chunk = fp.read(chunk_size)
                if not data_chunk:
                    break

                file_hash.update(data_chunk)

        return f'"{file_hash.hexdigest()}"'
