import json
from typing import Optional
from typing import TypeVar, Generic, List
from base64 import b64decode, b64encode

from fastapi import HTTPException, Query, status
from pydantic import generics, Field
from humps import camelize


MAX_PAGE_SIZE = 999
DEFAULT_PAGE_SIZE = 200


class PaginationDetails():
    """
    A representation of the pagination details that can be included within the query string.

    """

    def __init__(self, cursor: Optional[str] = None, page_size: Optional[int] = None):
        self.offset = 0
        self.page_size = max(min(page_size or DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE), 0)

        if cursor:
            try:
                self.offset = decode_cursor(cursor)
            except ValueError as error:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    def next_cursor(self):
        """
        Get the cursor for the next page of results - assumes that a next page exists.

        """
        return encode_cursor(self.offset + min(self.page_size, MAX_PAGE_SIZE))

    def previous_cursor(self):
        """
        Get the cursor for the previous page of results.

        """
        if self.offset <= 0:
            return None
        return encode_cursor(max(self.offset - min(self.page_size, MAX_PAGE_SIZE), 0))


def decode_cursor(cursor: str):
    """
    Decodes a cursor which can be included within the query parameters.

    """

    try:
        return int(json.loads(b64decode(cursor).decode('utf-8'))['offset'])
    except Exception:
        raise ValueError(f'Invalid cursor: {cursor}')


def encode_cursor(offset: int):
    """
    Encodes a cursor which can be included within the query parameters.

    """

    return b64encode(json.dumps({'offset': offset}).encode('utf-8')).decode('utf-8')


DataT = TypeVar('DataT')


class PaginatedResults(generics.GenericModel, Generic[DataT]):

    next: Optional[str] = Field(None, description=(
        'The url to use to retrieve the next page of results.'
    ), example='https://api.example.com/widgets?cursor=V2VsbCBhcmV1IGN1cmlvdXM=')
    previous: Optional[str] = Field(None, description=(
        'The url to use to retrieve the previous page of results.'
    ), example='https://api.example.com/widgets?cursor=5SFSDGcmlvdDFGXM=')
    results: List[DataT] = Field(..., description=(
        'A list of the current page of results.'
    ))

    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


"""
A representation of the query parameter required to specify the cursor within a request.

"""
CURSOR_QUERY = Query(
    None,
    description=(
        'The cursor indicating a unique page of results - this should be auto generated on '
        'the `next` and `previous` fields and does not need to be manually added / updated.'
    ),
    example='V2VsbCBhcmVuJ3QgeW91IGN1cmlvdXM=',
)


"""
A representation of the query parameter required to specify the page size.

"""
PAGE_SIZE_QUERY = Query(
    None,
    description=(
        'The number of results to return per page. This is limited to 999 results, if a '
        'number over 999 is provided the results will be capped at 999. Defaults to 200.'
    ),
    example=500,
)
