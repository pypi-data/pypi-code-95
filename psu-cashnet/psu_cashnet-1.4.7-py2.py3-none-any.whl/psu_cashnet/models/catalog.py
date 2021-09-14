from django.db import models
from datetime import datetime
from psu_base.classes.Log import Log
from psu_base.classes.ConvenientDate import ConvenientDate

log = Log()


class CatalogItem(models.Model):
    """Item definitions"""

    date_created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    last_updated = models.DateTimeField(blank=True, null=True, auto_now=True)

    app_code = models.CharField(
        max_length=15,
        verbose_name="Application Code",
        help_text="Application that this catalog item belongs to.",
        blank=False,
        null=False,
    )
    item_code = models.CharField(
        max_length=80,
        help_text="Item code used within the Django app",
        blank=False,
        null=False,
    )
    cashnet_code = models.CharField(
        max_length=80,
        help_text="Item code as defined in Cashnet",
        blank=False,
        null=False,
    )
    gl = models.CharField(
        max_length=30,
        help_text="GL code in Cashnet (usually blank)",
        default=None,
        blank=True,
        null=True,
    )
    description = models.CharField(
        max_length=128, help_text="Description of the item", blank=False, null=False
    )
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=6,  # Max price: 9,999.99
        help_text="Price of this item",
        blank=False,
        null=False,
    )

    # Sale amount overrides regular amount when:
    #   * No date range is defined
    #   * After sale start date (null start date starts immediately)
    #   * Before sale end date (null end date never ends)
    sale_amount = models.DecimalField(
        decimal_places=2,
        max_digits=6,  # Max price: 9,999.99
        help_text="Reduced price of this item",
        default=None,
        blank=True,
        null=True,
    )
    sale_start_date = models.DateTimeField(blank=True, null=True)
    sale_end_date = models.DateTimeField(blank=True, null=True)

    def sale_start_date_input(self):
        return ConvenientDate(self.sale_start_date).timestamp().replace(" ", "T")

    def sale_end_date_input(self):
        return ConvenientDate(self.sale_end_date).timestamp().replace(" ", "T")

    def sale_date_notice(self):
        if self.is_on_sale() and self.sale_end_date:
            return f"Sale ends {ConvenientDate(self.sale_end_date).humanized()}"
        elif self.is_future_sale():
            return f"Sale starts {ConvenientDate(self.sale_start_date).humanized()}"
        elif self.is_past_sale():
            return f"Sale ended {ConvenientDate(self.sale_end_date).humanized()}"
        else:
            return ""

    def is_future_sale(self):
        return self.sale_start_date and self.sale_start_date >= datetime.now()

    def is_past_sale(self):
        return self.sale_end_date and self.sale_end_date < datetime.now()

    def is_on_sale(self):

        # To be on sale, a sale amount is required
        if self.sale_amount is None:
            return False

        # If sale starts in future, then not currently on sale
        if self.sale_start_date and self.sale_start_date >= datetime.now():
            return False

        # If sale ended, then not currently on sale
        if self.sale_end_date and self.sale_end_date < datetime.now():
            return False

        return True

    def current_price(self):
        return self.sale_amount if self.is_on_sale() else self.amount

    def current_price_as_percent(self):
        return f"{int(self.current_price() * 100)}%"

    def current_price_description(self):
        if self.current_price is None:
            return ""
        elif self.current_price and self.current_price < 1:
            return "{0:.0f}%".format(self.current_price * 100)
        else:
            return "${0:.2f}".format(self.current_price * 100)

    def amount_description(self):
        if self.amount is None:
            return ""
        elif self.amount and self.amount < 1:
            return "{0:.0f}%".format(self.amount * 100)
        else:
            return "${0:,.2f}".format(self.amount)

    def __str__(self):
        return f"[{self.item_code}: {self.current_price()}]"

    @classmethod
    def get(cls, pk):
        try:
            return cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            return None
