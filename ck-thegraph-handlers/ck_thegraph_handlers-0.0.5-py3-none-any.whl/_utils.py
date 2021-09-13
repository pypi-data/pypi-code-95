from decimal import Decimal
from typing import AsyncGenerator, List, TypeVar, Union

Number = Union[int, float, Decimal]
SupportsNumber = Union[str, Number]

div_safe_default = Decimal("0")


def div_safe(
    num: SupportsNumber,
    denom: SupportsNumber,
    default: Decimal = div_safe_default,
) -> Decimal:
    """Divide two numbers. If denominator is zero, return `default`."""
    denom = safe_decimal(denom)
    return safe_decimal(num) / denom if denom != 0 else default


def safe_decimal(number: SupportsNumber) -> Decimal:
    """
    Try to convert any number-like object to Decimal.
    Suited mostly for floats:
    >>> Decimal(1.01)
    Decimal('1.0100000000000000088817841970012523233890533447265625')
    >>> Decimal('1.01')
    Decimal('1.01')
    """
    if isinstance(number, Decimal):
        return number
    elif isinstance(number, float):
        return Decimal(str(number))
    elif isinstance(number, (int, str)):
        return Decimal(number)
    else:
        raise TypeError(f"Type {type(number)} is not supported.")


A = TypeVar("A")


async def alist(agen: AsyncGenerator[A, None]) -> List[A]:
    """
    Since asynchronous generators are not awaitable by themselves, materialize
    them by this coroutine.

    async def my_asyngen():
        yield 1
        yield 2

    This call is illegal:
    await my_asyncgen()

    This works:
    res = await alist(my_asyncgen())
    assert res == [1, 2]
    """
    return [i async for i in agen]
