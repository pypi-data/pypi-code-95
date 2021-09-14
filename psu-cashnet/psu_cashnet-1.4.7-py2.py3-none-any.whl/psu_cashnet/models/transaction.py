from django.db import models
from psu_base.classes.Log import Log
from psu_base.services import auth_service, utility_service
from urllib.parse import urlencode
from django.urls import reverse

log = Log()


class Transaction(models.Model):
    """Item definitions"""

    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    app_code = models.CharField(
        max_length=15,
        verbose_name="Application Code",
        help_text="Application that this transaction belongs to.",
        blank=False,
        null=False,
        db_index=True,
    )

    # Keep multiple customer identifiers for search features
    customer_username = models.CharField(
        max_length=30, blank=False, null=False, db_index=True
    )
    customer_psu_id = models.CharField(
        max_length=9, blank=False, null=False, db_index=True
    )
    customer_name = models.CharField(max_length=120, blank=False, null=False)

    # Get customer identity object
    def customer(self):
        return auth_service.look_up_user_cache(self.customer_username)

    # PSU's merchant code must be configured with CASHNET in advance.
    merchant_code = models.CharField(max_length=30, blank=False, null=False)
    # For encoded digest. Must be configured with CASHNET in advance.
    secret_key = models.CharField(max_length=80, default=None, blank=True, null=True)

    status_code = models.CharField(
        max_length=1,
        help_text="Status of the transaction",
        blank=False,
        null=False,
        default="N",
        db_index=True,
    )
    initiation_date = models.DateTimeField(blank=True, null=True)
    response_date = models.DateTimeField(blank=True, null=True)

    admin_updated = models.CharField(
        max_length=30,
        help_text="Username of admin that changed status",
        blank=True,
        null=True,
    )
    admin_updated_date = models.DateTimeField(blank=True, null=True)

    duplicate_count = models.IntegerField(blank=False, null=False, default=0)
    duplicate_date = models.DateTimeField(blank=True, null=True)

    term_code = models.CharField(
        max_length=6,
        help_text="Optional term code",
        default=None,
        blank=True,
        null=True,
    )
    success_url = models.CharField(
        max_length=80,
        help_text="URL name to redirect to after successful payment",
        blank=False,
        null=False,
    )
    failure_url = models.CharField(
        max_length=80,
        help_text="URL name to redirect to after incomplete payment",
        blank=False,
        null=False,
    )

    reference_class = models.CharField(
        max_length=80,
        help_text="If transaction is linked to another Django model",
        default=None,
        blank=True,
        null=True,
    )
    reference_id = models.IntegerField(
        help_text="If transaction is linked to another Django model",
        default=None,
        blank=True,
        null=True,
    )
    post_processing_status = models.CharField(
        max_length=30,
        help_text="If additional processing required after payment, describe status here",
        default=None,
        blank=True,
        null=True,
    )

    # Cashnet Response Values
    # =========================================================================
    cashnet_result_code = models.IntegerField(
        help_text="Result from cashnet. 0 is success. All others are failure.",
        default=None,
        blank=True,
        null=True,
    )
    cashnet_result_message = models.CharField(
        max_length=256, default=None, blank=True, null=True
    )
    cashnet_error_code = models.CharField(
        max_length=30, default=None, blank=True, null=True
    )
    cashnet_error_message = models.CharField(
        max_length=256, default=None, blank=True, null=True
    )
    cashnet_transaction = models.CharField(
        max_length=30, default=None, blank=True, null=True
    )
    cashnet_batch = models.CharField(max_length=30, default=None, blank=True, null=True)
    # =========================================================================
    result_parameters = models.CharField(
        max_length=500, default=None, blank=True, null=True
    )
    internal_error_message = models.CharField(
        max_length=256, default=None, blank=True, null=True
    )

    @property
    def status_options(self):
        return {
            'R': 'Recorded',
            'I': 'Initiated',
            'P': 'Processing',
            'E': 'Error',
            'N': 'New',
            'S': 'Success',
            'F': 'Failure',
        }

    def status_desc(self):
        return self.status_options.get(self.status_code, 'Unknown')

    def is_recorded(self):
        return self.status_code == "R"

    def was_processed(self):
        return self.status_code in ["S", "F"]

    def was_successful(self):
        return self.status_code == "S"

    def was_failure(self):
        return self.status_code == "F"

    def had_error(self):
        return self.status_code == "E"

    def status_can_be_updated(self):
        return self.status_code in ["R", "I", "P", "E", "N"]

    def items(self):
        return self.purchaseditem_set.all()

    def num_items(self):
        return len(self.items())

    def total_amount(self):
        total = 0
        for ii in self.items():
            total += ii.purchase_qty_amount()
        return total

    def cashnet_fake_url_base(self):
        return reverse("cashnet:fake_cashnet", args=[self.id])

    def cashnet_train_url_base(self):
        return f"https://train.cashnet.com/{self.merchant_code}"

    def cashnet_prod_url_base(self):
        return f"https://commerce.cashnet.com/{self.merchant_code}"

    def cashnet_url(self, force_train=False, force_fake=False):
        if utility_service.is_non_production():
            # For local development, only the fake site will work (train/prod redirect to AWS)
            if utility_service.is_development():
                url = self.cashnet_fake_url_base()
            # Can only force train site from stage (redirect goes to stage)
            elif force_train:
                url = self.cashnet_train_url_base()
            elif force_fake or utility_service.get_setting(
                "CASHNET_SIMULATE_TRANSACTION"
            ):
                url = self.cashnet_fake_url_base()
            else:
                url = self.cashnet_train_url_base()
        else:
            # Train and Fake sites are never allowed in prod
            url = self.cashnet_prod_url_base()

        return f"{url}?{self.cashnet_parameter_string()}"

    def cashnet_parameter_string(self):
        return urlencode(self.cashnet_parameters())

    def cashnet_parameters(self):
        # Customer info
        c = self.customer()

        parameters = {
            "ref1type1": "TRANSACTION_ID",
            "ref1val1": self.id,
            "custcode": c.psu_id,
            "fname": c.first_name,
            "lname": c.last_name,
            "email": c.email_address,
        }

        # Items
        ii = 1

        def add_one_item(seq, fee):
            # Item Code is always required
            parameters.update({f"itemcode{ii}": item.catalog_item.cashnet_code})
            # Item amount may be defined in Cashnet
            if item.purchase_amount:
                parameters.update(
                    {f"amount{ii}": "{0:.2f}".format(item.purchase_qty_amount())}
                )
            # Item GL code is optional
            if item.catalog_item.gl:
                parameters.update({f"gl{ii}": item.catalog_item.gl})

        for item in self.items():
            # Items with pre-defined prices in Cashnet will need to be listed multiple times when qty > 1
            if item.qty > 1 and not item.purchase_amount:
                for qq in range(0, item.qty):
                    add_one_item(ii, item)
                    ii += 1
            # All other items get one set of parameters
            else:
                add_one_item(ii, item)
                ii += 1

        return parameters

    def set_post_processing_status(self, status):
        self.post_processing_status = status[:30] if status else status

    def __str__(self):
        return f"[tx:{self.id}-{self.total_amount()}-{self.status_code}]"

    @classmethod
    def get(cls, pk):
        try:
            return cls.objects.get(pk=pk)
        except cls.DoesNotExist:
            return None
