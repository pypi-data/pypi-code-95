from io import BytesIO
from pathlib import Path
from typing import (
    Any,
    List,
    Mapping,
    Optional,
    Union,
)

import numpy as np
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.string_description import StringDescription
from sklearn.externals import joblib

from microcosm_sagemaker.testing.bytes_extractor import ExtractorMatcherPair


class IsObjectEqual(BaseMatcher):
    """
    Matcher to compare the object A with another object B.
    Sometimes there is some randomness within these generated files, so the user can optionally
    provide a `ignore_properties` array which will ignore mismatches of those given object
    properties.  For instance, if we have:
    MyObject(foo=bar, extras=Test)
    MyObject(foo=bar, extras=Test2)
    If ignore_properties is not specified, these will be unequal.  If ignore_properties is
    set to ["extras"], they will be equal.

    """
    def __init__(self, obj: Any, ignore_properties: List = []) -> None:
        self.ignore_properties = ignore_properties
        self.compare_object = obj

    def _matches(self, item: Any) -> bool:
        compare_a = self._get_dict_structure(self.compare_object)
        compare_b = self._get_dict_structure(item)

        total_attributes = (
            attr
            for attr in set(compare_a.keys()) | set(compare_b.keys())
            if attr not in self.ignore_properties
        )

        for attr in total_attributes:

            if attr not in compare_a or attr not in compare_b:
                return False

            if type(compare_a[attr]) != type(compare_b[attr]):  # noqa: 721
                return False

            if isinstance(compare_a[attr], np.ndarray):
                if (compare_a[attr] != compare_b[attr]).any():
                    return False
            elif compare_a[attr] != compare_b[attr]:
                return False

        return True

    def describe_to(self, description: StringDescription) -> None:
        description.append_text(str(self.compare_object))

    def _get_dict_structure(self, obj: Any) -> Mapping[str, Any]:
        if isinstance(obj, dict):
            return obj
        # the matcher expects a dictionary in the _matches method
        # -> we convert the set into a dictionary with a dummy key
        elif isinstance(obj, set):
            return dict(dummy_attrb=obj)
        return vars(obj)


def pickle_extractor(binary: bytes) -> Any:
    return joblib.load(BytesIO(binary))


def matches_object(
    obj: Union[object, dict],
    ignore_properties: Optional[List[str]] = None,
) -> IsObjectEqual:
    if ignore_properties is None:
        ignore_properties = []
    return IsObjectEqual(obj, ignore_properties)


def matches_with_object(obj: Any) -> IsObjectEqual:
    return matches_object(obj)


def _get_dir_pickles(dir: Path, pickle_suffixes: List[str]) -> List[Path]:
    return [
        subpath.relative_to(dir)
        for subpath in dir.glob("**/*")
        if subpath.suffix in pickle_suffixes
    ]


def _create_matchers(dir_pickles: List[Path]) -> Mapping[Path, ExtractorMatcherPair]:
    return {
        path: ExtractorMatcherPair(
            pickle_extractor,
            matches_with_object,
        )
        for path in dir_pickles
    }


def create_pickle_matchers_for_dir(dir, pickle_suffixes=[".pk", ".pickle", ".pkl"]):
    dir_pickles = _get_dir_pickles(dir, pickle_suffixes)
    matchers = _create_matchers(dir_pickles)
    return matchers
