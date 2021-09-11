from enum import Enum


class FieldType(str, Enum):
    DNA_SEQUENCE_LINK = "dna_sequence_link"
    AA_SEQUENCE_LINK = "aa_sequence_link"
    CUSTOM_ENTITY_LINK = "custom_entity_link"
    ENTITY_LINK = "entity_link"
    MIXTURE_LINK = "mixture_link"
    DROPDOWN = "dropdown"
    PART_LINK = "part_link"
    TRANSLATION_LINK = "translation_link"
    BLOB_LINK = "blob_link"
    TEXT = "text"
    LONG_TEXT = "long_text"
    BATCH_LINK = "batch_link"
    STORAGE_LINK = "storage_link"
    ENTRY_LINK = "entry_link"
    ASSAY_REQUEST_LINK = "assay_request_link"
    ASSAY_RESULT_LINK = "assay_result_link"
    ASSAY_RUN_LINK = "assay_run_link"
    BOOLEAN = "boolean"
    FLOAT = "float"
    INTEGER = "integer"
    DATETIME = "datetime"
    DATE = "date"
    JSON = "json"

    def __str__(self) -> str:
        return str(self.value)
