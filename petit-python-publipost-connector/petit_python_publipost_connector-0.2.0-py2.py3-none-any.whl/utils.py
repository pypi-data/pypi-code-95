import io


def download_minio_stream(stream, _file: io.BytesIO) -> None:
    for d in stream.stream(32*1024):
        _file.write(d)