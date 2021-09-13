from itertools import groupby
from typing import List, Dict

from NEMO.models import Consumable, Tool
from NEMO.rates import Rates
from django.conf import settings
from django.utils.formats import number_format

from NEMO_billing.rates.models import Rate


class DatabaseRates(Rates):
    def __init__(self):
        self.currency = getattr(settings, "RATE_CURRENCY", "$")

    def load_rates(self):
        pass

    def get_consumable_rates(self, consumables: List[Consumable]) -> Dict[str, str]:
        return {
            rate.consumable.name: self.consumable_rate_display(rate)
            for rate in Rate.objects.filter(consumable__in=consumables)
        }

    def get_consumable_rate(self, consumable: Consumable) -> str:
        consumable_rate = Rate.objects.get(consumable=consumable)
        if consumable_rate.exists():
            return self.consumable_rate_display(consumable_rate)

    def get_tool_rate(self, tool: Tool) -> str:
        tool_rates = Rate.objects.filter(tool=tool).order_by("type", "category")
        list_by_type = groupby(tool_rates, key=lambda x: x.type)
        return "<br>".join(
            [
                f"{rate_type.get_type_display()}: {self.tool_rate_display_by_category(tool_rates)}"
                for rate_type, tool_rates in list_by_type
            ]
        )

    def tool_rate_display_by_category(self, rates: List[Rate]):
        return ", ".join(
            [
                f"<b>{self.display_amount(rate.amount)}</b>{' (' + rate.category.name + ')' if rate.category else ''}"
                for rate in rates
            ]
        )

    def consumable_rate_display(self, rate: Rate) -> str:
        return f"<b>{self.display_amount(rate.amount)}</b>"

    def display_amount(self, amount):
        return f"{self.currency}{number_format(amount, decimal_pos=2)}"
