from typing import TypedDict, Any, Dict, Optional


class JsonLDDocument(TypedDict):
    """Loaded document."""

    document: Dict[str, Any]
    contextUrl: Optional[str]
