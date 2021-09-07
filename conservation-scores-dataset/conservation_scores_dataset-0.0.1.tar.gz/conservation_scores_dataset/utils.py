"""Utilities for easier usage."""
from typing import List
import compress_json


def get_available_conservation_scores(assembly: str = "hg38") -> List[str]:
    """Return conservation scores available for the provided genomic assembly.

    Parameters
    --------------------------
    assembly: str = "hg38",
        The genomic assembly to retrieve.
    """
    return list(compress_json.local_load("urls.json")[assembly])


def get_available_conservation_score_versions(
    assembly: str = "hg38",
    conservation_score: str = "phastCons"
) -> List[str]:
    """Return conservation scores available for the provided genomic assembly.

    Parameters
    --------------------------
    assembly: str = "hg38",
        The genomic assembly to retrieve.
    conservation_score: str = "phastCons",
        The conservation score whose available versions are to be retrieved.
    """
    return list(compress_json.local_load("urls.json")[assembly][conservation_score])
