from decimal import Decimal
from logging import getLogger

from NEMO.models import Tool, Area, Consumable, User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.db import models
from django.db.models import QuerySet
from mptt.fields import TreeForeignKey

from NEMO_billing.rates.model_diff import ModelDiff

model_logger = getLogger(__name__)


class ActionLog(object):
    ADD = 0
    DELETE = 1
    UPDATE = 2
    Choices = ((ADD, "Add"), (DELETE, "Delete"), (UPDATE, "Update"))


class RateCategory(models.Model):
    name = models.CharField(max_length=200, help_text="The name of this rate category")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Rate category"
        verbose_name_plural = "Rate categories"


class RateType(models.Model):
    class Type(object):
        TOOL = "Tool"
        TOOL_USAGE = "TOOL_USAGE"
        TOOL_TRAINING_INDIVIDUAL = "TOOL_TRAINING_INDIVIDUAL"
        TOOL_TRAINING_GROUP = "TOOL_TRAINING_GROUP"
        TOOL_MISSED_RESERVATION = "TOOL_MISSED_RESERVATION"
        AREA = "Area"
        AREA_USAGE = "AREA_USAGE"
        AREA_MISSED_RESERVATION = "AREA_MISSED_RESERVATION"
        CONSUMABLE = "CONSUMABLE"
        STAFF_CHARGE = "STAFF_CHARGE"
        choices = [
            (
                TOOL,
                (
                    (TOOL_USAGE, "Tool usage"),
                    (TOOL_TRAINING_INDIVIDUAL, "Tool individual training"),
                    (TOOL_TRAINING_GROUP, "Tool group training"),
                    (TOOL_MISSED_RESERVATION, "Tool missed reservation"),
                ),
            ),
            (AREA, ((AREA_USAGE, "Area usage"), (AREA_MISSED_RESERVATION, "Area missed reservation"))),
            (CONSUMABLE, "Consumable/Supply"),
            (STAFF_CHARGE, "Staff charge"),
        ]

    type = models.CharField(max_length=100, choices=Type.choices)
    category_specific = models.BooleanField(
        default=False,
        help_text="Check this box to make this rate type category specific (i.e. you will need to enter a rate for each category)",
    )
    item_specific = models.BooleanField(
        default=False,
        help_text="Check this box to make this rate type item specific (i.e. you will need to enter a rate for each item)",
    )

    def is_tool_rate(self):
        return self.type in [
            self.Type.TOOL_MISSED_RESERVATION,
            self.Type.TOOL_USAGE,
            self.Type.TOOL_TRAINING_INDIVIDUAL,
            self.Type.TOOL_TRAINING_GROUP,
        ]

    def is_area_rate(self):
        return self.type in [self.Type.AREA_USAGE, self.Type.AREA_MISSED_RESERVATION]

    def is_consumable_rate(self):
        return self.type == self.Type.CONSUMABLE

    def is_staff_charge_rate(self):
        return self.type == self.Type.STAFF_CHARGE

    def get_rate_group_type(self) -> str:
        if self.is_tool_rate() and self.item_specific:
            return RateType.Type.TOOL
        elif self.is_area_rate() and self.item_specific:
            return RateType.Type.AREA
        else:
            return self.type

    def get_type_form_name(self, category: RateCategory = None):
        # name to use in forms to identify
        name = str(self.type).lower()
        if self.category_specific and category:
            name = name + "_" + category.name.lower()
        return name

    def __str__(self):
        return self.get_type_display()


class Rate(models.Model):
    type = models.ForeignKey(RateType, on_delete=models.CASCADE)
    category = models.ForeignKey(RateCategory, null=True, blank=True, on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool, null=True, blank=True, on_delete=models.CASCADE)
    area = TreeForeignKey(Area, null=True, blank=True, on_delete=models.CASCADE)
    consumable = models.ForeignKey(Consumable, null=True, blank=True, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=8, help_text="The rate per hour if this isn't a flat rate")
    flat = models.BooleanField(default=False, help_text="Check this box to make this a flat rate (independent of time)")
    minimum_charge = models.DecimalField(decimal_places=2, max_digits=8, null=True, blank=True, help_text="The minimum charge for this rate")

    def get_item(self):
        if self.type.is_tool_rate():
            return self.tool
        elif self.type.is_area_rate():
            return self.area
        elif self.type.is_consumable_rate():
            return self.consumable
        elif self.type.is_staff_charge_rate():
            return "Staff charge"

    get_item.short_description = "Item"

    def clean(self):
        errors = {}
        if self.type_id:
            if self.type.is_tool_rate():
                if self.area or self.consumable:
                    errors[NON_FIELD_ERRORS] = ValidationError(
                        "You cannot select an area or a consumable for a tool rate"
                    )
                if self.type.item_specific and not self.tool:
                    errors["tool"] = ValidationError("You need to select a tool for this rate type")
            elif self.type.is_area_rate():
                if self.tool or self.consumable:
                    errors[NON_FIELD_ERRORS] = ValidationError(
                        "You cannot select a tool or a consumable for a area rate"
                    )
                if self.type.item_specific and not self.area:
                    errors["area"] = ValidationError("You need to select an area for this rate type")
            elif self.type.is_consumable_rate():
                if self.tool or self.area:
                    errors[NON_FIELD_ERRORS] = ValidationError(
                        "You cannot select a tool or an area for a consumable rate"
                    )
                if self.type.item_specific and not self.consumable:
                    errors["consumable"] = ValidationError("You need to select a consumable for this rate type")
                if not self.flat:
                    errors["flat"] = ValidationError("Consumable rates are flat rates")
            elif self.type.is_staff_charge_rate():
                if self.tool or self.consumable or self.area:
                    errors[NON_FIELD_ERRORS] = ValidationError(
                        "You cannot select a tool, area or consumable for a staff charge rate"
                    )
            if not self.type.item_specific and (self.tool or self.consumable or self.area):
                errors[NON_FIELD_ERRORS] = ValidationError(
                    "You cannot select a tool, area or consumable for a non item specific rate type"
                )
            if RateCategory.objects.exists() and self.type.category_specific and not self.category:
                errors["category"] = ValidationError("This rate type is category specific. Please select a category")
            if not self.type.category_specific and self.category:
                errors["category"] = ValidationError("The rate type you selected is not category specific")
        if errors:
            raise ValidationError(errors)

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)
        if exclude and "type" not in exclude and self.type:
            # Essentially a type that is category_specific but no categories exist is the same as non category specific
            category_specific = self.type.category_specific and RateCategory.objects.exists()
            if not category_specific and not self.type.item_specific:
                rate_already_exists = Rate.objects.filter(type=self.type).exclude(pk=self.pk).exists()
                if rate_already_exists:
                    raise ValidationError("A rate of this type already exists")
            elif not category_specific and self.type.item_specific:
                rate_already_exists = (
                    self.rate_item_filter(Rate.objects.filter(type=self.type)).exclude(pk=self.pk).exists()
                )
                if rate_already_exists:
                    raise ValidationError(f"A rate of this type already exists for {self.get_item()}")
            elif category_specific and self.type.item_specific:
                rate_already_exists = (
                    self.rate_item_filter(Rate.objects.filter(type=self.type, category=self.category))
                    .exclude(pk=self.pk)
                    .exists()
                )
                if rate_already_exists:
                    raise ValidationError(
                        f"A rate of this type already exists for {self.get_item()} and category {self.category}"
                    )
            elif category_specific and not self.type.item_specific:
                rate_already_exists = (
                    Rate.objects.filter(type=self.type, category=self.category).exclude(pk=self.pk).exists()
                )
                if rate_already_exists:
                    raise ValidationError(f"A rate of this type already exists for category {self.category}")

    def rate_item_filter(self, queryset: QuerySet) -> QuerySet:
        if self.type:
            if self.type.is_tool_rate():
                return queryset.filter(tool=self.tool)
            elif self.type.is_area_rate():
                return queryset.filter(area=self.area)
            elif self.type.is_consumable_rate():
                return queryset.filter(consumable=self.consumable)
        return queryset

    # Use this method instead of regular save to allow rates audit log
    def save_with_user(self, user: User, force_insert=False, force_update=False, using=None, update_fields=None):
        try:
            rate_pre_save_log(self, user)
        except Exception as e:
            model_logger.exception(e)
        super().save(force_insert, force_update, using, update_fields)

    def delete_with_user(self, user: User, using=None, keep_parents=False):
        try:
            rate_pre_delete_log(self, user)
        except Exception as e:
            model_logger.exception(e)
        return super().delete(using, keep_parents)

    def is_hourly_rate(self):
        return self.type.type in [
            RateType.Type.TOOL_USAGE,
            RateType.Type.AREA_USAGE,
            RateType.Type.STAFF_CHARGE,
            RateType.Type.TOOL_TRAINING_GROUP,
            RateType.Type.TOOL_TRAINING_INDIVIDUAL,
        ]

    def display_rate(self) -> str:
        amount = f"{self.amount:.2f}"
        if self.is_hourly_rate():
            if self.flat:
                # Display flat explicitly when we have a hourly rate set as flat
                amount = f"flat {amount}"
            else:
                # Display hourly when we have an hourly rate not set as flat
                amount = f"{amount}/hr"
        minimum = f" ({self.minimum_charge:.2f} minimum)" if self.minimum_charge else ""
        return f"{amount}{minimum}"

    def calculate_amount(self, quantity: Decimal) -> Decimal:
        effective_quantity = quantity
        if self.is_hourly_rate():
            if self.flat:
                # If hourly rate is set as flat, disregard quantity
                effective_quantity = 1
            else:
                # Otherwise divide by 60 since quantity is in minutes
                effective_quantity = quantity / Decimal(60)
        amount = effective_quantity * self.amount
        if self.minimum_charge:
            amount = max(amount, self.minimum_charge)
        return amount

    def __str__(self):
        item_name = f"{self.get_item()} " if self.get_item() else ""
        category = self.category if self.category else ""
        return f"{item_name}{self.type} {category}"


class RateLog(models.Model):
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.SET_NULL)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey("content_type", "object_id")
    action = models.IntegerField(choices=ActionLog.Choices)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    details = models.TextField(null=True, blank=True)


def get_rate_content_object(rate: Rate):
    item = rate.get_item()
    return item if isinstance(item, models.Model) else None


def rate_pre_save_log(rate: Rate, user: User, **kwargs):
    try:
        original: Rate = Rate.objects.get(pk=rate.pk)
    except Rate.DoesNotExist:
        RateLog.objects.create(
            action=ActionLog.ADD,
            user=user,
            content_object=get_rate_content_object(rate),
            details=ModelDiff(rate).model_diff_display,
        )
    else:
        model_diff = ModelDiff(original, rate)
        if model_diff.has_changed():
            RateLog.objects.create(
                action=ActionLog.UPDATE,
                user=user,
                content_object=get_rate_content_object(original),
                details=model_diff.model_diff_display,
            )


def rate_pre_delete_log(rate: Rate, user: User, **kwargs):
    RateLog.objects.create(
        action=ActionLog.DELETE,
        user=user,
        content_object=get_rate_content_object(rate),
        details=ModelDiff(rate).model_diff_display,
    )
