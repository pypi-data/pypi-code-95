"""Classification init module."""
import typing as t
from pathlib import Path

from dotty_dict import Dotty

from .block import Block
from .profile import Profile
from .rule import Action, Match, Rule

__all__ = ["Action", "Block", "Profile", "Match", "Rule", "run_classification"]


def run_classification(
    profile_or_path: t.Union[Path, Profile], i_dict: t.Dict[str, t.Any]
) -> t.Tuple[bool, Dotty]:
    """Run classification and generate dictionary.

    Args:
        p_path (Path, Profile): Path to profile or instantiated Profile.
        i_dict (Dict[str, Any]): Input dictionary.

    Returns:
        (bool): True if any block executed, False otherwise.
        (Dict[str, Any]): Output Dotty dictionary.
    """
    if hasattr(profile_or_path, "evaluate"):
        profile = profile_or_path
    else:
        profile = Profile(Path(profile_or_path))  # type: ignore
    res, out = profile.evaluate(i_dict)  # type: ignore
    return res, out
