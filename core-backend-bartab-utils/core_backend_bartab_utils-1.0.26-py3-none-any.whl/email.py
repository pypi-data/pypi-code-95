from email_validator import validate_email as email_validator, EmailNotValidError
from rest_framework.serializers import ValidationError


def get_protected_email(
    s): return '@'.join(x[0]+'*'*(len(x)-2)+x[-1] for x in s.split('@'))


def validate_email(email):
    try:
        # Validate.
        email_validator(email)
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        raise ValidationError('{} is not a valid email'.format(email))
