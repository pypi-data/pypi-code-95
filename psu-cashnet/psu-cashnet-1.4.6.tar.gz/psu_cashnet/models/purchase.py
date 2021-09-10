from django.db import models
from psu_base.classes.Log import Log

log = Log()


class PurchasedItem(models.Model):
    """Item definitions"""

    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    transaction = models.ForeignKey("Transaction", on_delete=models.CASCADE)
    catalog_item = models.ForeignKey("CatalogItem", on_delete=models.DO_NOTHING)

    # Since catalog item price can change, record actual price paid
    purchase_amount = models.DecimalField(
        decimal_places=2,
        max_digits=6,  # Max price: 9,999.99
        help_text="Price paid for this item",
        blank=False,
        null=False,
    )

    qty = models.IntegerField(blank=False, null=False, default=1)

    def purchase_qty_amount(self):
        if self.purchase_amount:
            return self.purchase_amount * self.qty
        else:
            return self.purchase_amount

    def __str__(self):
        return f"[{self.catalog_item.item_code}: {self.purchase_qty_amount}]"

    @classmethod
    def get(cls, pk):
        try:
            return cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            return None
