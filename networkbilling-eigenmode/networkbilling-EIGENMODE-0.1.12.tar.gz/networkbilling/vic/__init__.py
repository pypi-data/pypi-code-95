from typing import Any
import networkbilling.vic.invoice as invoice
import networkbilling.vic.dispute as dispute
import networkbilling.vic.remittance as remittance


def header_mapping(record_type: int) -> Any:
    to_fn = {
        10: invoice.Invoice,
        910: dispute.Dispute,
        920: remittance.Remittance
    }
    return to_fn[record_type]
