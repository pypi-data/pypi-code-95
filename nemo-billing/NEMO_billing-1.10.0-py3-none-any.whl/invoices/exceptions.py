from NEMO.exceptions import NEMOException
from NEMO.models import Tool, Area, Consumable, Project
from NEMO_billing.invoices.models import Invoice, InvoiceDetailItem

from NEMO_billing.rates.models import RateCategory, RateType


class NoRateSetException(NEMOException):
    def __init__(
        self,
        rate_type_id: int,
        category: RateCategory = None,
        tool: Tool = None,
        area: Area = None,
        consumable: Consumable = None,
    ):
        self.rate_type = RateType.objects.get(id=rate_type_id)
        self.category = category
        self.tool = tool
        self.area = area
        self.consumable = consumable
        for_category = f" for category: {category}" if category else ""
        for_item = (
            f" for: {tool if tool else area if area else consumable if consumable else ''}"
            if tool or area or consumable
            else ""
        )
        msg = f"No {self.rate_type.get_type_display()} rate is set{for_item}{for_category}"
        super().__init__(msg)


class NoProjectDetailsSetException(NEMOException):
    def __init__(self, project: Project):
        self.project = project
        msg = f"There are no project details set for project {project.name}"
        super().__init__(msg)


class InvoiceAlreadyExistException(NEMOException):
    def __init__(self, invoice: Invoice):
        self.invoice = invoice
        msg = f"An invoice ({invoice.invoice_number}) already exist for this project for this date range. Void it to be able to generate it again"
        super().__init__(msg)


class InvoiceItemsNotInFacilityException(NEMOException):
    def __init__(self, item: InvoiceDetailItem):
        self.item = item
        item_type_display = item.get_item_type_display().replace("_", " ")
        msg = f"Error generating invoice. A {item_type_display}: {item.name} for user {item.user} is not part of any core facilities"
        super().__init__(msg)
