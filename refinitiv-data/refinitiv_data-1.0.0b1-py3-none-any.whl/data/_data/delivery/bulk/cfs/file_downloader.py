from ._cfs_provider import CFSProvider, CFSFile
from ._file_downloader import _FileDownloader
from ._unpacker import _Unpacker
from .... import log
from ....tools._common import cached_property

__all__ = ["Definition"]

logger = log.root_logger.getChild("file-downloader")


class FileDownloader:
    def __init__(self, url, filename_ext) -> None:
        self._url = url
        self._filename_ext = filename_ext
        self._downloaded_filepath = None

    @cached_property
    def _downloader(self) -> _FileDownloader:
        return _FileDownloader(logger)

    @cached_property
    def _unpacker(self) -> _Unpacker:
        return _Unpacker(logger)

    def download(self, path="") -> "FileDownloader":
        self._downloaded_filepath = self._downloader.download(
            self._url, self._filename_ext, path
        )
        return self

    def extract(self, path="") -> str:
        filepath = self._downloaded_filepath or self._filename_ext
        extracted_filepath = self._unpacker.unpack(filepath, path)
        return extracted_filepath


class Definition:
    def __init__(self, file: CFSFile):
        self._file_id = file["id"]
        self._filename_ext = file["filename"]

    def retrieve(self, session=None) -> FileDownloader:
        provider = CFSProvider(session=session)
        stream = provider.get_stream(self._file_id)
        raw = stream.data.raw

        if raw.get("error", None):
            raise ValueError(raw["error"]["message"])

        url = raw.get("url", None)

        if not url:
            raise FileNotFoundError("file not found")

        return FileDownloader(url, self._filename_ext)
