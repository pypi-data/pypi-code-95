from typing import Any
import networkbilling.sa.invoice as invoice
import networkbilling.sa.dispute as dispute
import networkbilling.sa.remittance as remittance
import networkbilling.sa.servicecharge as servicecharge


def header_mapping(record_type: int) -> Any:
    to_fn = {
        10: invoice.Invoice,
        910: dispute.Dispute,
        920: remittance.Remittance,
        12: servicecharge.Servicecharge
    }
    return to_fn[record_type]
