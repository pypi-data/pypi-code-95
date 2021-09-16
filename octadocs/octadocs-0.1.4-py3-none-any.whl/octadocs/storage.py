from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from documented import DocumentedError
from octadocs.octiron import Octiron


@dataclass
class CacheNotFound(DocumentedError):
    """
    Cache file not found.

    File Path: {self.file_path}

    To create the cache, please run `mkdocs serve` or `mkdocs build`.
    """

    file_path: Path


@dataclass
class DiskCacheStorage:
    """Store the graph content on disk to support CLI queries."""

    octiron: Octiron
    directory: Optional[Path] = None
    format: str = 'json-ld'

    def _file_name(self) -> str:
        """Construct the file name."""
        return f'octadocs.{self.format}'

    def _file_path(self) -> Path:
        """Construct path to the file."""
        return (
            self.directory or
            self.octiron.root_directory.parent / '.cache'
        ) / self._file_name()

    def save(self) -> None:
        """Store graph contents on disk."""
        graph_content = self.octiron.graph.serialize(
            format=self.format,
        ).decode()

        try:
            self._file_path().write_text(graph_content)
        except FileNotFoundError:
            self._file_path().parent.mkdir(parents=True, exist_ok=True)
            self._file_path().write_text(graph_content)

    def load(self) -> None:
        """Load graph content from file."""
        try:
            graph_content = self._file_path().read_text()
        except FileNotFoundError:
            raise CacheNotFound(
                file_path=self._file_path(),
            )

        self.octiron.graph.parse(
            data=graph_content,
            format=self.format,
        )
