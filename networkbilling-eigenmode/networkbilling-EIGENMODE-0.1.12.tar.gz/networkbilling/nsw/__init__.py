from typing import Any
import networkbilling.nsw.invoice as invoice
import networkbilling.nsw.remittance as remittance
import networkbilling.nsw.dispute as dispute
import networkbilling.nsw.statuschange as statuschange
import networkbilling.nsw.outstanding as outstanding
import networkbilling.nsw.creditbalance as creditbalance


def header_mapping(record_type: int) -> Any:
    to_fn = {
        10: invoice.Invoice,
        800: remittance.Remittance,
        910: dispute.Dispute,
        913: statuschange.Statuschange,
        930: outstanding.Outstanding,
        940: creditbalance.Creditbalance
    }
    return to_fn[record_type]
