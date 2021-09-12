import logging
from dataclasses import dataclass
from typing import Dict, Any, List

from pyld.jsonld import JsonLdError

from octadocs.pyld_document_loaders.base import DocumentLoader
from octadocs.pyld_document_loaders.models import JsonLDDocument

logger = logging.getLogger(__name__)


@dataclass
class ChoiceLoader(DocumentLoader):
    """Choose the first loader in the list which works."""

    loaders: List[DocumentLoader]

    def __call__(self, url: str, options: Dict[str, Any]) -> JsonLDDocument:
        """Try each loader in the sequence."""
        if not self.loaders:
            raise JsonLdError(
                message=(
                    'Please specify at least one loader '
                    'for ChoiceLoader to choose from.'
                ),
                type_='jsonld.InvalidUrl',
                details={'url': url},
                code='loading document failed',
            )

        errors = []
        for loader in self.loaders:
            try:
                return loader(url=url, options=options)
            except JsonLdError as err:
                errors.append(err)

        raise JsonLdError(
            message=f'None of the loaders could process URL: {url}',
            type_='jsonld.InvalidUrl',
            details={
                'url': url,
                'errors': errors,
            },
            code='loading document failed',
        )
