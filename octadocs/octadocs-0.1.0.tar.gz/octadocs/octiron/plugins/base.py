from pathlib import Path
from typing import Iterator, Optional, Any, Dict

import rdflib
from octadocs.types import Context, Triple


class Loader:
    """Data importer for Octiron."""

    # Which files is this loader working with?
    regex: str

    # Absolute path to source file
    path: Path

    # Local address of the file, which will be used as graph name
    local_iri: rdflib.URIRef

    # The URL of the page (relative or absolute) under which the page will be
    # accessible for users.
    global_url: Optional[str]

    # JSON-LD context
    context: Context

    # Named contexts from Octiron config
    named_contexts: Dict[str, Any]

    def __init__(
        self,
        path: Path,
        local_iri: rdflib.URIRef,
        global_url: Optional[str],
        context: Context,
        named_contexts: Dict[str, Any],
    ) -> None:
        """Initialize the data loader."""
        self.path = path
        self.context = context
        self.local_iri = local_iri
        self.global_url = global_url
        self.named_contexts = named_contexts

    def stream(self) -> Iterator[Triple]:
        """Read the source data and return a stream of triples."""
        raise NotImplementedError()
