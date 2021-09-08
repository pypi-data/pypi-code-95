import re
from typing import Optional, Tuple

from .countries import COUNTRY_MAP


def is_vies_member(country_code: str) -> bool:
    """
    The abbreviations to use are the ISO codes, except for Greece and the United Kingdom
    """
    if not re.match(r"^[a-zA-Z]{2}$", country_code):
        raise ValueError("Invalid code")

    country_code = country_code.upper()
    if country_code == "GR":
        # http://publications.europa.eu/code/pdf/370000en.htm
        raise ValueError("Use EL for Greece")

    if country_code == "GB":
        # https://ec.europa.eu/taxation_customs/sites/taxation/files/use_of_gb_and_xi_codes_guidance.pdf
        raise ValueError(
            "Use XI for Northern Ireland and XU for United Kingdom (excluding Northern Ireland)"
        )

    return country_code in COUNTRY_MAP


def parse_number(value: str) -> Optional[Tuple[str, str]]:
    value = value.replace(" ", "").upper()
    country_code = value[:2]
    number = value[2:]

    validator = COUNTRY_MAP.get(country_code, None)
    if validator:
        if validator.match(value):
            return country_code, number

    return None
