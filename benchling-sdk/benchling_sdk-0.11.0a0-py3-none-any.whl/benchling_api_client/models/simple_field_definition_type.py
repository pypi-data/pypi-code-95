from enum import Enum


class SimpleFieldDefinitionType(str, Enum):
    DNA_SEQUENCE_LINK = "dna_sequence_link"
    AA_SEQUENCE_LINK = "aa_sequence_link"
    CUSTOM_ENTITY_LINK = "custom_entity_link"
    MIXTURE_LINK = "mixture_link"
    BLOB_LINK = "blob_link"
    TEXT = "text"
    LONG_TEXT = "long_text"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    DATE = "date"
    JSON = "json"

    def __str__(self) -> str:
        return str(self.value)
