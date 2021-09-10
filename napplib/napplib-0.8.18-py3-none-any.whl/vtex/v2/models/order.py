from dataclasses import dataclass
from typing import List
from enum import Enum
from typing import Optional

class VtexOrderInvoiceType(Enum):
    OUTPUT = "Output"
    INPUT = "Input"

@dataclass
class VtexOrderInvoiceItem:
    id: str
    quantity: int
    price: int

@dataclass
class VtexOrderInvoice:
    type: VtexOrderInvoiceType
    invoiceNumber: float
    invoiceValue: int
    invoiceUrl: str
    invoiceKey: str
    issuanceDate: str
    items: Optional[List[VtexOrderInvoiceItem]] = None