import re


# Patterns: https://ec.europa.eu/taxation_customs/vies/faq.html#item_11
COUNTRY_MAP = {
    # Austria
    "AT": re.compile(r"^ATU\d{8}$"),
    # Belgium
    "BE": re.compile(r"^BE[0,1]\d{9}$"),
    # Bulgaria
    "BG": re.compile(r"^BG\d{9,10}$"),
    # Cyprus
    "CY": re.compile(r"^CY\d{8}[A-Z]$"),
    # Czech Republic
    "CZ": re.compile(r"^CZ\d{8,10}$"),
    # Germany
    "DE": re.compile(r"^DE\d{9}$"),
    # Denmark
    "DK": re.compile(r"^DK\d{8}$"),
    # Estonia
    "EE": re.compile(r"^EE\d{9}$"),
    # Greece
    "EL": re.compile(r"^EL\d{9}$"),
    # Spain - # The first and last characters may be alpha or numeric; but they may not both be numeric.
    "ES": re.compile(r"^ES[A-Z0-9]\d{7}[A-Z0-9]$"),
    # Finland
    "FI": re.compile(r"^FI\d{8}$"),
    # France
    "FR": re.compile(r"^FR[A-Z0-9]{2}\d{9}$"),
    # Croatia
    "HR": re.compile(r"^HR\d{11}$"),
    # Hungary
    "HU": re.compile(r"^HU\d{8}$"),
    # Ireland
    "IE": re.compile(r"^IE\d[A-Z0-9\+\*]\d{5}[A-Z]{1,2}$"),
    # Italy
    "IT": re.compile(r"^IT\d{11}$"),
    # LT
    "LT": re.compile(r"^LT(\d{9}|\d{12})$"),
    # Luxembourg
    "LU": re.compile(r"^LU\d{8}$"),
    # Latvia
    "LV": re.compile(r"^LV\d{11}$"),
    # Malta
    "MT": re.compile(r"^MT\d{8}$"),
    # Netherlands
    "NL": re.compile(r"^NL[A-Z0-9\+\*]{12}$"),
    # Poland
    "PL": re.compile(r"^PL\d{10}$"),
    # Portugal
    "PT": re.compile(r"^PT\d{9}$"),
    # Romania
    "RO": re.compile(r"^RO\d{2,10}$"),
    # Sweden
    "SE": re.compile(r"^SE\d{12}$"),
    # Slovenia
    "SI": re.compile(r"^SI\d{8}$"),
    # Slovakia
    "SK": re.compile(r"^SK\d{10}$"),
    # Northern Ireland
    "XI": re.compile(r"^XI(?:\d{9}(?:\d{3})?|GD\d{3}|HA\d{3})$"),
    # "GB" United Kingdom (left on 31 January 2020)
}
