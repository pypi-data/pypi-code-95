from dataclasses import dataclass
from typing import List
from enum import Enum
from typing import Optional

class VtexInvoiceType(Enum):
    OUTPUT = "Output"
    INPUT = "Input"

@dataclass
class VtexInvoiceItem:
    id: str
    quantity: int
    price: int

@dataclass
class VtexInvoice:
    type: VtexInvoiceType
    invoiceNumber: float
    invoiceValue: int
    invoiceUrl: str
    invoiceKey: str
    issuanceDate: str
    items: Optional[List[VtexInvoiceItem]] = None