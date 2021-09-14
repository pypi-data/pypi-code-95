"""Base adapter class."""
import abc
import typing as t
from pathlib import Path

from dotty_dict import Dotty

from .. import Profile, run_classification


class Adapter(abc.ABC):  # pragma: no cover
    """Abstract class to handle needed pre/post-processing for classification.

    This class calls `classify.run` but also provides abstract `preprocess`
    and `postprocess` methods to allow for fine-grained logic for specific
    objects or file types.

    For example, an adaptor may be written that extracts the header from
    a new file type, and prepares it as a dictionary needed by `classify.run`.
    """

    def __init__(self, file) -> None:
        """Initialize adapter with file."""
        self.file = file

    @abc.abstractmethod
    def preprocess(self) -> t.Dict[str, t.Any]:
        """Create dictionary representation of object."""
        raise NotImplementedError

    @abc.abstractmethod
    def postprocess(self, res: bool, out: Dotty) -> t.Any:
        """Handle output doing any needed postprocessing."""
        raise NotImplementedError

    def classify(self, profile: t.Union[Profile, Path]) -> t.Any:
        """Run classification with particular adapter."""
        i_dict = self.preprocess()
        res, out = run_classification(profile, i_dict)
        return self.postprocess(res, out)
