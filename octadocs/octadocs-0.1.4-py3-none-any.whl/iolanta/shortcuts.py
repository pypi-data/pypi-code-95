from typing import Type

from urlpath import URL

from iolanta.loaders import Loader, LocalFile
from iolanta.models import LDDocument


def choose_loader_by_url(url: URL) -> Type[Loader]:
    """Find loader by URL scheme."""
    return LocalFile


def as_document(url: URL) -> LDDocument:
    """Retrieve the document presented by the specified URL."""
    loader_class = choose_loader_by_url(url)
    return loader_class().as_jsonld_document(url)
