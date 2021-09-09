from typing import Literal, Union

import math

import numpy as np

Ascending = Literal["ascending"]
Descending = Literal["descending"]
SortAction = Union[Ascending, Descending]


def rolling(
    usd_available: int, values: np.ndarray, percentage_to_fill: float, sort: SortAction = Ascending
) -> np.ndarray:
    """Calculates the number of shares we can buy for each stock on a rolling basis decided by the sort

    Args:
    -----------
    usd_available: int
        The total profilio amount available to spend.
    values: np.ndarray
        The list of stocks prices.
    percentage_to_fill: float
        The max percentage of the profilio value to buy shares for any one stock
    sort: SortAction
        The sorting order of values [ascending: smallest->biggest, descending: biggest->smallest]

    Examples
    -----------
    >>> stock_prices = np.array([10.0, 50.0, 20.0])
    >>> available_positions = rolling(100.0, stock_prices, .50, sort="ascending")
    >>> available_positions
    array([5, 2])

    Returns:
    -----------
    numpy.ndarray
        [positions_available_to_fill]
    """
    # Sort the stock prices using quicksort algorithm
    sorted_values = np.sort(values.astype(float), axis=0, kind="quicksort")
    # If rolling in descending order, reverse the array
    if sort == "descending":
        sorted_values = sorted_values[::-1]
    # Make the available profilio amount a float to work with math.floor
    f_amount = float(usd_available)
    # The rolling amount used to keep track of current profolio balance
    r_amount = f_amount
    # Stores the positions to buy results
    positions = []
    # Iterate over the current prices
    for _, position_price in np.ndenumerate(sorted_values):
        # Never calculate if position_price is over the profolio rolling amount
        if r_amount > position_price:
            positions_available_to_fill = math.floor(f_amount * percentage_to_fill / position_price)
            r_amount -= positions_available_to_fill * position_price
            positions.append(positions_available_to_fill)
    return np.array(positions)
