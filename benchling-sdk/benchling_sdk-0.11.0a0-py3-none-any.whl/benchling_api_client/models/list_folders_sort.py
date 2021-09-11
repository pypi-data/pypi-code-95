from enum import Enum


class ListFoldersSort(str, Enum):
    MODIFIEDAT = "modifiedAt"
    NAME = "name"
    MODIFIEDATASC = "modifiedAt:asc"
    NAMEASC = "name:asc"
    MODIFIEDATDESC = "modifiedAt:desc"
    NAMEDESC = "name:desc"

    def __str__(self) -> str:
        return str(self.value)
