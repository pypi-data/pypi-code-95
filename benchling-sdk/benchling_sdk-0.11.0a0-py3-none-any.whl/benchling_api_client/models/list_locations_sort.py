from enum import Enum


class ListLocationsSort(str, Enum):
    BARCODE = "barcode"
    MODIFIEDAT = "modifiedAt"
    NAME = "name"
    BARCODEASC = "barcode:asc"
    MODIFIEDATASC = "modifiedAt:asc"
    NAMEASC = "name:asc"
    BARCODEDESC = "barcode:desc"
    MODIFIEDATDESC = "modifiedAt:desc"
    NAMEDESC = "name:desc"

    def __str__(self) -> str:
        return str(self.value)
