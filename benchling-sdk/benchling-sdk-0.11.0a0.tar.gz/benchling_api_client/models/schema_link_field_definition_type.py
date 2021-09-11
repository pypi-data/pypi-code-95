from enum import Enum


class SchemaLinkFieldDefinitionType(str, Enum):
    ENTITY_LINK = "entity_link"
    ENTRY_LINK = "entry_link"
    PART_LINK = "part_link"
    TRANSLATION_LINK = "translation_link"
    BATCH_LINK = "batch_link"
    STORAGE_LINK = "storage_link"
    ASSAY_REQUEST_LINK = "assay_request_link"
    ASSAY_RESULT_LINK = "assay_result_link"
    ASSAY_RUN_LINK = "assay_run_link"

    def __str__(self) -> str:
        return str(self.value)
