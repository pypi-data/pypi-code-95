from datetime import datetime

INVOICE_DATE_FORMAT = "%B %d, %Y"
INVOICE_DATETIME_FORMAT = "%m/%d/%Y %H:%M:%S"
INVOICE_EMAIL_SUBJECT_PREFIX = "[NEMO Billing] "

INVOICE_ALL_ITEMS_MUST_BE_IN_FACILITY = False

# Display all months since this date in generate invoice page
INVOICE_MONTH_LIST_SINCE = datetime(year=2021, month=1, day=1)
