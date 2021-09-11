from typing import Any, cast, Dict, List, Type, TypeVar

import attr

T = TypeVar("T", bound="AutoAnnotateDnaSequences")


@attr.s(auto_attribs=True, repr=False)
class AutoAnnotateDnaSequences:
    """  """

    _dna_sequence_ids: List[str]
    _feature_library_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("dna_sequence_ids={}".format(repr(self._dna_sequence_ids)))
        fields.append("feature_library_ids={}".format(repr(self._feature_library_ids)))
        return "AutoAnnotateDnaSequences({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dna_sequence_ids = self._dna_sequence_ids

        feature_library_ids = self._feature_library_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "dnaSequenceIds": dna_sequence_ids,
                "featureLibraryIds": feature_library_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        dna_sequence_ids = cast(List[str], d.pop("dnaSequenceIds"))

        feature_library_ids = cast(List[str], d.pop("featureLibraryIds"))

        auto_annotate_dna_sequences = cls(
            dna_sequence_ids=dna_sequence_ids,
            feature_library_ids=feature_library_ids,
        )

        return auto_annotate_dna_sequences

    @property
    def dna_sequence_ids(self) -> List[str]:
        return self._dna_sequence_ids

    @dna_sequence_ids.setter
    def dna_sequence_ids(self, value: List[str]) -> None:
        self._dna_sequence_ids = value

    @property
    def feature_library_ids(self) -> List[str]:
        return self._feature_library_ids

    @feature_library_ids.setter
    def feature_library_ids(self, value: List[str]) -> None:
        self._feature_library_ids = value
