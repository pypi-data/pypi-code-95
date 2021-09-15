"""
Introduction
------------
Cursor objects are return by the Client.sql() API.
A cursor simply binds the query to a particular collection and the
query is not executed server side until the application starts to fetch
results from the cursor.

.. note:: Cursors are never instantiated directly by the application \
and are always instantiated by Rockset Client ``sql()`` APIs.

Fetch all results
-----------------

Use the cursor's results() method to fetch all the results of the query
in one shot::

    results = mycollection.sql(q).results()

The above technique will work well, if the number of results returned by the
query is limited, say because it employs a LIMIT clause.

For queries, that return a large number of results, please use the cursor
iterators as described below.

Iterators with automatic pagination
-----------------------------------

Cursor objects are iterables, so you can do something like::

    results = mycollection.sql(q)
    for r in results:
        print(r)

Cursor objects support seamless automatic pagination to iterate over large
result sets. The cursor iterator will fetch and buffer a small portion of the
results and as the iterator reaches the end of the current batch of buffered
results, it will automatically issue the query with the appropriate pagination
parameters to buffer the next batch and seamlessly continue results iteration.

The default cursor iterator uses a batch size of 10,000. You can create a cursor
iterator with a different batch size by using the ``iter()`` method.

Example using the default cursor iterator::

    results = mycollection.sql(q)
    for r in results:
        print(r)


Example using a custom cursor iterator with batch size 200::

    results = mycollection.sql(q)
    for r in results.iter(200):
        print(r)

.. automethod:: rockset.Cursor.iter()

Async requests
--------------

Cursors support asyncio.Future to schedule and run queries concurrently
along with other async events in your application.

One can create an asyncio.Future from a cursor object using the
``Cursor.async_request()`` method. These futures are not scheduled in
any async threads and the application have to schedule them in an asyncio
event loop. Once the futures are scheduled and run to completion, then
the results of their respective queries can be accessed by calling
future.result(). The return value of future.result() will be identical
to calling Cursor.results() API on the original query.

For example::

    jims_future = people.sql(F["first_name"] == "Jim").async_request()
    sfmerch_future = merchants.sql(F["zipcode"] == "94107").async_request()

    # can schedule these asyncio.futures along with other futures
    # issue both queries concurrently and block until both of them finish
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(jims_future, sfmerch_future))

    all_jims = jims_future.result()
    all_sfmerchants = sfmerch_future.result()

Even if an future was originally issued by an async_requst() API call,
one can still call the blocking Cursor.results() API to fetch the results
synchronously. Cursor.results() will schedule the future, block until the
future finishes execution and then will return those results. A subsequent
future.result() call will return the query results immediately.

For example::

    jims_cursor = people.sql(F["first_name"] == "Jim")
    jims_future = jims_cursor.async_request()

    # do a blocking results() will block on the future behind the scenes
    results = jims_cursor.results()

    # this will return immediately without incurring any server round-trip
    results2 = jims_future.result()


.. automethod:: rockset.Cursor.async_request()

"""

from rockset.document import Document
from rockset.exception import ServerError, InputError
from rockset.query import LimitQuery, SubQuery
from rockset.swagger_client.api.queries_api import QueriesApi
from rockset.swagger_client.models.query_request import QueryRequest
from rockset.swagger_client.models.query_response import QueryResponse

import asyncio
import sys


class Cursor(object):
    """ Fetch the results of a query executed against a collection
    """
    def __init__(
        self, q=None, client=None, generate_warnings=False, timeout=None
    ):
        self._query = q
        self._client = client
        self._lastq_response = None
        self._fullq_response = None
        self._future = None
        self._warnings = None
        self._generate_warnings = generate_warnings
        self._timeout = timeout

    def _run(self):
        if self._fullq_response is None:
            self._fullq_response = self._run_query()
        return self._fullq_response

    def _execute_query(self, request):
        """Keep all backend interaction within this function,
        so that it is easy to mock in tests"""
        # execute query
        qreq = QueryRequest(sql=request)
        response = QueriesApi(self._client
                             ).query(qreq, _request_timeout=self._timeout)
        if not isinstance(response, QueryResponse):
            raise ServerError(
                message='invalid return message (type={} results={})'.
                format(type(response), response)
            )
        return response

    def _run_query(self, limit=None, skip=0):
        # add limit, offset to query if required
        query = self._query
        if limit is not None:
            query = LimitQuery(
                limit=limit, skip=skip, child=SubQuery(query, alias='subq')
            )

        # build the query request object
        request = {}
        (sqltxt, params) = query.sql()
        request = {
            'query': sqltxt,
            'parameters': params.sqlparams(),
        }

        # Only add this parameters if `_generate_warnings` is set to True.
        # This is to ensure that if apiserver is not pushed, not requesting
        # warnings still works.
        # TODO(hieup): Put `generate_warnings` to `qo` once we push apiserver
        if self._generate_warnings:
            request['generate_warnings'] = True

        self._lastq_response = self._execute_query(request)
        return self._lastq_response

    def _get_docs(self, response):
        if not response.results:
            return []
        return [Document(row) for row in response.results]

    def __iter__(self):
        return self.iter()

    def __str__(self):
        return str(self.results())

    def __getitem__(self, key):
        return self.results()[key]

    def iter(self, batch=10000):
        """ Returns an iterator that does seamless automatic pagination
        behind the scenes while fetching no more than the specified
        batch size number of results at a time.

        Args:
            batch (int): maximum number of results fetched at a time

        Returns:
            Iterator Object: Iterator that will return all results one \
            :class:`Document` object at a time with automatic pagination
        """
        if batch <= 0:
            raise InputError(
                message='invalid cursor iterator batchsize. "{}" is not '
                'a positive integer.'.format(batch)
            )

        skip = 0
        while True:
            results = self._get_docs(self._run_query(batch, skip))
            for r in results:
                yield r
            if ((batch is None) or (batch > len(results))):
                break
            skip += batch

    def results(self):
        """ Execute the query and fetch all the results in one shot.

        Returns:
            list[:class:`Document`]: Results of the query represent as a list
            of Document objects
        """
        return self._get_docs(self._run())

    def warnings(self):
        """ Retrieve warnings that occurred during query execution, if any.

        Returns:
            list[str]: The warnings from the query. Returns None if no warnings exist.
        """
        return self._lastq_response and self._lastq_response.warnings

    def rowcount(self):
        """Number of rows returned by the last query

        Returns:
            int: The number of rows that the last query produced.
            Returns None in case no query has been executed yet.
        """
        return self._lastq_response and len(self._lastq_response.results)

    def fields(self):
        """ Once query has been executed, this method will return all the
        fields that are present in the query result, while preserving
        the order in which those fields were selected in the input query.

        NOTE: this method will return None when called before the query has
              actually been executed.

        Returns:
            list[dicts]: List of column headers in the query result,
                            preserving the ordering from the input query.
        """
        if not self._lastq_response:
            raise InputError(
                message='cannot call fields() before query execution'
            )

        # server will return field names in the order the query requested
        # for all queries except 'SELECT * FROM ...'
        columns = None
        if self._lastq_response.column_fields:
            columns = [cf['name'] for cf in self._lastq_response.column_fields]

        # TODO: come up with a better way to do this
        # get all results and infer schema from them
        # build a row with all possible fields, by merging all into one
        # remove this once apiserver returns both field names and types
        schema = Document()
        for r in self._get_docs(self._run()):
            schema.update(r)

        return schema.fields(columns=columns)

    def stats(self):
        """Query execution stats

        Returns:
            dict: Some key execution stats
            Returns None in case no query has been executed yet.
        """
        return self._lastq_response and self._lastq_response.stats

    def async_request(self):
        """ Returns an asyncio.Future object that can be scheduled in an
        asyncio event loop. Once scheduled and run to completion, the results
        can be fetched via the future.result() API. The return value of
        future.result() will be the same as the return value of Cursor.results()

        Returns:
            asyncio.Future: Returns a Future object that can be scheduled
            in an asyncio event loop and future.result() will hold the same
            return value as Cursor.results()
        """
        if self._future is not None:
            return self._future
        self._future = asyncio.Future()
        asyncio.ensure_future(self._issue())
        return self._future

    async def _issue(self):
        self._future.set_result(self.results())


__all__ = [
    'Cursor',
]
