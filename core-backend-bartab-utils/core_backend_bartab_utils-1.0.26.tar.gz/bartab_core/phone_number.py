import phonenumbers
from rest_framework.serializers import ValidationError


def validate_phone_number(phone_number):
    try:
        phone_number_obj = phonenumbers.parse(phone_number, None)
        if not phonenumbers.is_possible_number(phone_number_obj) or not phonenumbers.is_valid_number(phone_number_obj):
            raise ValidationError(
                {'phone_number': [phone_number+' is not a valid phone number']})
    except ValidationError as exp:
        raise exp
    except phonenumbers.NumberParseException as exp:
        raise ValidationError(
            {'phone_number': ['Phone number invalid, format: +11234567890']})
    except Exception as exp:
        raise exp


def is_valid_phone_number(phone_number: str) -> bool:
    try:
        validate_phone_number(phone_number)
        return True
    except:
        return False


def get_protected_phone_number(phone_number: str) -> str:
    if is_valid_phone_number(phone_number):
        len_phone_number_no_nation = len(phone_number)
        phone_number_end = phone_number[len_phone_number_no_nation -
                                                  4: len_phone_number_no_nation]

        return f"+1******{phone_number_end}"
    raise ValueError("Invalid phone number")
