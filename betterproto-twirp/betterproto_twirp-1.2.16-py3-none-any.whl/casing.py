import keyword

import stringcase


def safe_snake_case(value: str) -> str:
    """Snake case a value taking into account Python keywords."""
    value = stringcase.snakecase(value)
    value = sanitize_name(value)
    return value


def sanitize_name(value):
    return f"{value}_" if keyword.iskeyword(value) else value
