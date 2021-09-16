from typing import Any
import networkbilling.qld.invoice as invoice
import networkbilling.qld.remittance as remittance
import networkbilling.qld.dispute as dispute
import networkbilling.qld.statuschange as statuschange
import networkbilling.qld.outstanding as outstanding
import networkbilling.qld.creditbalance as creditbalance
import networkbilling.qld.servicecharge as servicecharge


def header_mapping(record_type: int) -> Any:
    to_fn = {
        10: invoice.Invoice,
        800: remittance.Remittance,
        910: dispute.Dispute,
        913: statuschange.Statuschange,
        930: outstanding.Outstanding,
        940: creditbalance.Creditbalance,
        12: servicecharge.Servicecharge
    }
    return to_fn[record_type]
