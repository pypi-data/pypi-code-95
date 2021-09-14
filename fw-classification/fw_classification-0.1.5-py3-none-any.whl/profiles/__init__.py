"""Module to hold yaml profiles."""
from pathlib import Path

PROFILES = Path(__file__).parents[0]


def get_profile(name: str) -> Path:
    """Get a specific profile by name.

    Args:
        name (str): Name of the profile.

    Returns:
        Path: Path to the profile

    Raises:
        ValueError: If the specified profile doesn't exist.
    """
    profile = PROFILES / name
    if not profile.exists():
        raise ValueError(f"Could not find profile {name}")
    return profile
