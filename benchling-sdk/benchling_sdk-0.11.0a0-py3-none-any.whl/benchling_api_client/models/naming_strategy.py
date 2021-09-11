from enum import Enum


class NamingStrategy(str, Enum):
    NEW_IDS = "NEW_IDS"
    IDS_FROM_NAMES = "IDS_FROM_NAMES"
    DELETE_NAMES = "DELETE_NAMES"
    SET_FROM_NAME_PARTS = "SET_FROM_NAME_PARTS"
    REPLACE_NAMES_FROM_PARTS = "REPLACE_NAMES_FROM_PARTS"
    KEEP_NAMES = "KEEP_NAMES"
    REPLACE_ID_AND_NAME_FROM_PARTS = "REPLACE_ID_AND_NAME_FROM_PARTS"

    def __str__(self) -> str:
        return str(self.value)
