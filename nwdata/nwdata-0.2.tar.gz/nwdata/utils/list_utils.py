from functools import reduce
from typing import Iterable, List, T

def flattenList(x : Iterable[List[T]]) -> List[T]:
	return reduce(lambda a, b : a + b, x)
