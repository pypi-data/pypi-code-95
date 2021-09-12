from typing import List, Union


def convert_str_to_int_or_none(s: str) -> Union[int, None]:
    if s == "None":
        return None
    return int(s)


def convert_int_or_none_to_str(v: Union[int, None]) -> str:
    if v is None:
        return "None"
    return str(v)


def convert_str_to_int(s: str) -> int:
    return int(s)


def convert_str_to_int_default(i: int, s: str) -> int:
    if s.startswith("+"):
        return i + int(s[1:])
    if s.startswith("-"):
        return i - int(s[1:])
    if s.startswith("*"):
        return i * int(s[1:])
    if s.startswith("/"):
        return i // int(s[1:])
    assert False, "you should not get here"


def convert_int_to_str(i: int) -> str:
    return str(i)


def convert_str_to_bool(s: str) -> bool:
    if s in {"TRUE", "true", "True", "yes", "Yes", "1", "y", "Y", "t", "T"}:
        return True
    return False


def convert_bool_to_str(b: bool) -> str:
    return str(b)


def convert_str_to_list_int(s: str) -> List[int]:
    return [int(x) for x in s.split(",")]


def convert_list_int_to_str(li: List[int]) -> str:
    return ",".join([str(x) for x in li])


def convert_str_to_list_str(s: str) -> List[str]:
    return s.split(",")


def convert_list_str_to_str(li: List[str]) -> str:
    return ",".join(li)


def convert_str_to_str(e: str) -> str:
    return e


def convert_str_to_str_or_none(s: str) -> Union[str, None]:
    if s == "None":
        return None
    return s


def convert_str_or_none_to_str(v: Union[str, None]) -> str:
    if v is None:
        return "None"
    return v
