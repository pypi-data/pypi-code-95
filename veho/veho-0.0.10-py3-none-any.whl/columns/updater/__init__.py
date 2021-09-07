from typing import List, Any


def unshift_column(mx: List[List[Any]], column: List[Any]):
    h = len(mx)
    for i in range(h): mx[i].insert(0, column[i])
    return mx


def shift_column(mx: List[List[Any]]):
    return [row.pop(0) for row in mx]


def push_column(mx: List[List[Any]], column: List[Any]):
    h = len(mx)
    for i in range(h): mx[i].append(column[i])
    return mx


def pop_column(mx: List[List[Any]]):
    return [row.pop() for row in mx]
