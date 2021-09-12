from typing import Dict, Any

from octadocs.pyld_document_loaders.models import JsonLDDocument


class DocumentLoader:
    """Load a document by URL."""

    def __call__(self, url: str, options: Dict[str, Any]) -> JsonLDDocument:
        """Execute the loading itself."""
        raise NotImplementedError()
