"""
Usage
-----
Query Lambdas are named parameterized and versioned SQL queries
stored in Rockset and can be executed through a dedicated HTTPS endpoint.

Example
-------
::

    from rockset import Client, Q

    # connect securely to Rockset
    rs = Client()

    # create a Query Lambda
    qlambda = rs.QueryLambda.create(
        'myQueryLambda',
        query=Q('SELECT 1'))

    # print details about Query Lambda
    print(qlambda.workspace, qlambda.name, qlambda.version, qlambda.query)

    # execute a Query Lambda
    results = qlambda.execute()
    print(results)

.. _QueryLambda.create:

Create a new Query Lambda
-------------------------
Creating a Query Lambda using the Client_ object is as simple as
calling ``rs.QueryLambda.create('myQueryLambda', query=Q('SELECT...'))``::

    from rockset import Client, Q, F, P
    rs = Client()

    # construct a parameterized query
    q = Q('_events').where(F['type'] == P['target_type']).limit(100)

    # set default value for query parameter
    q.P['target_type'] = 'INFO'

    # create a new Query Lambda
    qlambda = rs.QueryLambda.create(
        'myQueryLambda',
        workspace='commons',
        query=q,
    )

.. _QueryLambda.list:

List all Query Lambdas
----------------------
List all Query Lambdas using the Client_ object using::

    from rockset import Client
    rs = Client()

    # List latest version of all Query Lambdas across all workspaces
    qlambdas = rs.QueryLambda.list()

    # List latest version of all Query Lambdas in a given workspace
    qlambdas = rs.QueryLambda.list(workspace='commons')

.. _QueryLambda.retrieveByTag:

Retrieve an existing Query Lambda version by a given tag
--------------------------------------------------------
Retrieve the version of a given Query Lambda associated with a given tag::

    from rockset import Client
    rs = Client()

    # retrieve Query Lambda
    qlambda = rs.QueryLambda.retrieveByTag(
        'myQueryLambda',
        tag='dev',
        workspace='commons')

.. _QueryLambda.retrieveByVersion:

Retrieve an existing Query Lambda version
-----------------------------------------
Retrieve a particular version of a given Query Lambda::

    from rockset import Client
    rs = Client()

    # retrieve Query Lambda
    qlambda = rs.QueryLambda.retrieveByVersion(
        'myQueryLambda',
        version='ac34bfg234ee',
        workspace='commons')

.. _QueryLambda.describe:

Describe an existing Query Lambda version
-----------------------------------------
Fetch all details about a particular version of a given Query Lambda::

    from rockset import Client
    rs = Client()

    # retrieve Query Lambda
    qlambda = rs.QueryLambda.retrieveByTag(
        'myQueryLambda',
        tag='dev',
        workspace='commons')

    # print all details about this Query Lambda version
    print(qlambda.describe())

.. _QueryLambda.execute:

Execute a specific Query Lambda version
--------------------------------------
Execute a Query Lambda version, optionally passing in parameters::

    from rockset import Client, ParamDict
    rs = Client()

    # retrieve Query Lambda
    qlambda = rs.QueryLambda.retrieveByTag(
        'myQueryLambda',
        tag='dev',
        workspace='commons')

    params = ParamDict()
    for target_type in ['INFO', 'DEBUG', 'WARN', 'ERROR']:
        params['target_type'] = target_type
        for result in qlambda.execute(parameters=params).results:
            print(target_type, result)

.. _QueryLambda.update:

Update a Query Lambda by creating a new version
-----------------------------------------------
Update the query associated with the Query Lambda by creating a
new version of it and optionally giving it a tag::

    from rockset import Client, Q, F, P, ParamDict
    rs = Client()

    # retrieve Query Lambda
    ql = rs.QueryLambda.retrieveByTag(
        'myQueryLambda',
        tag='dev',
        workspace='commons')

    # construct a new query
    q = (Q('_events')
        .where(
            (F['type'] == P['target_type']) &
            (F['userEmail'] == P['user_email'])
        )
        .limit(100)
    )

    # optionally, set default value for some or all of the query parameters
    q.P['target_type'] = 'INFO'

    # update Query Lambda
    # optionally, add a version tag at this time
    ql_new_version = ql.update(q, tag='dev')

    # execute the new Query Lambda for different user_emails
    params = ParamDict()
    for email in ['scott@rockset.com', 'veeve@rockset.com']:
        params['user_email'] = email
        results = ql_new_version.execute(params).results
        print(email, results)

.. _QueryLambda.tag:

Tag a version of a Query Lambda
-------------------------------
Apply a tag to a specific Query Lambda version::

    from rockset import Client
    rs = Client()

    # retrieve Query Lambda
    ql = rs.QueryLambda.retrieveByVersion(
        'myQueryLambda',
        version='ac34bfg234ee',
        workspace='commons')

    # add tag 'dev' to this Query Lambda version
    ql.tag('dev')

.. _QueryLambda.history:

List all versions of a Query Lambda
-----------------------------------
Fetch all versions of a given Query Lambda::

    from rockset import Client
    rs = Client()

    # retrieve Query Lambda
    ql = rs.QueryLambda.retrieveByTag(
        'myQueryLambda',
        tag='dev',
        workspace='commons')

    # fetch all versions of this Query Lambda
    all_qlambda_versions = ql.history()

.. _QueryLambda.drop:

Drop Query Lambda along with all previous versions
--------------------------------------------------
Use the ``drop()`` method to remove a Query Lambda permanently from Rockset.

.. note:: This is a permanent and non-recoverable operation. Beware.

::

    from rockset import Client
    rs = Client()

    qlambda = rs.QueryLambda.retrieveByVersion(
        'myQueryLambda',
        version='ac34bfg234ee',
        workspace='commons')
    qlambda.drop()

"""
from rockset.query import Q
from rockset.swagger_client.api import (QueryLambdasApi)
from rockset.swagger_client.models import (
    QueryLambda, QueryLambdaSql, CreateQueryLambdaRequest,
    CreateQueryLambdaTagRequest, UpdateQueryLambdaRequest,
    ExecuteQueryLambdaRequest, QueryParameter
)

import rockset


def _convert_query_to_qlsql(query):
    if not isinstance(query, rockset.Query):
        raise ValueError(
            "Input query of type `{}` is not supported. "
            "Please pass a valid rockset.Query object as input.".format(
                type(query)
            )
        )

    (sqltext, sqlparams) = query.sql()
    ql_params = []
    for param in sqlparams.sqlparams():
        ql_params.append(QueryParameter(**param))
    return QueryLambdaSql(query=sqltext, default_parameters=ql_params)


class QueryLambdaClient(object):
    def __init__(self, client):
        self._api = QueryLambdasApi(client)

    def create(
        self, name, query, workspace="commons", description=None, **kwargs
    ):
        # convert rockset.Query to QueryLambdaSql
        ql_sql = _convert_query_to_qlsql(query)

        # construct CreateQueryLambdaRequest
        request = CreateQueryLambdaRequest(
            name=name,
            description=description,
            sql=ql_sql,
        )

        # issue create api call
        ql_model = self._api.create(workspace=workspace,
                                    body=request).get('data')
        return QueryLambdaVersion(self._api, ql_model)

    def list(self, workspace=None):
        if workspace:
            # If workspace specified, list queries in that workspace
            ql_models = self._api.list_0(workspace=workspace).get('data')
        else:
            # Else list all queries across all workspaces in the org
            ql_models = self._api.list().get('data')
        return [QueryLambda(self._api, qlm) for qlm in ql_models]

    def retrieve(self, name, version=None, workspace='commons', **kwargs):
        if not version:
            raise ValueError('Query Lambda version not specified.')
        ql_model = self._api.get_0(
            workspace=workspace, query_lambda=name, version=version
        ).get('data')
        return QueryLambdaVersion(self._api, ql_model)

    def retrieveByVersion(
        self, name, version=None, workspace='commons', **kwargs
    ):
        return self.retrieve(name, version=version, workspace=workspace)

    def retrieveByTag(self, name, tag=None, workspace='commons', **kwargs):
        if not tag:
            raise ValueError('Query Lambda tag not specified.')
        ql_model = self._api.get(
            workspace=workspace, query_lambda=name, tag=tag
        ).get('data').get('version')
        return QueryLambdaVersion(self._api, ql_model)


class QueryLambda(rockset.swagger_client.models.QueryLambda):
    def __init__(self, api, model):
        super(QueryLambda, self).__init__(**model.to_dict())
        self._api = api
        self._model = model

    def history(self):
        """Returns the entire version history of this Query Lambda.

        Returns:
            list: List of QueryLambdaVersion objects each representing a particular
            version of this Query Lambda
        """
        ql_models = self._api.list_2(
            workspace=self.workspace, query_lambda=self.name
        ).get('data')
        return [QueryLambdaVersion(self._api, qlm) for qlm in ql_models]


class QueryLambdaVersion(rockset.swagger_client.models.QueryLambdaVersion):
    def __init__(self, api, model):
        super(QueryLambdaVersion, self).__init__(**model.to_dict())
        self._api = api
        self._model = model

        # pull out the required fields explicitly
        self._query = Q(model.sql.query)
        for param in model.sql.default_parameters:
            self._query.P[param.name] = param.value

    @property
    def query(self):
        """Returns the query as a rockset.Query object along with
        default parameters specified for this Query Lambda version.

        Returns:
            Query: a Query object that represents the backend query
            that will be run when this Query Lambda is executed.
        """
        return self._query

    def describe(self):
        """Returns all properties of the Query Lambda as a dict.

        Returns:
            dict: with all properties of the Query Lambda
        """
        return self.to_dict()

    def history(self):
        """Returns the entire version history of this Query Lambda.

        Returns:
            list: List of QueryLambdaVersion objects each representing a particular
            version of this Query Lambda
        """
        ql_models = self._api.list_2(
            workspace=self.workspace, query_lambda=self.name
        ).get('data')
        return [QueryLambdaVersion(self._api, qlm) for qlm in ql_models]

    def update(self, query, tag=None, description=None):
        """Updates the query associated with the Query Lambda and returns
        a new QueryLambda object that represents the newly created version of
        this Query Lambda. Optionally applies a tag to this new version.

        Args:
           query (Query): Query object using which a new version of this
           Query Lambda will be created.
           tag (str): Version tag that will be applied to the newly created version
           description (str): Human readable description that can be used as
           a commit message for this update.

        Returns:
            QueryLambdaVersion: a QueryLambdaVersion object that represents the new version
        """
        ql_sql = _convert_query_to_qlsql(query)
        request = UpdateQueryLambdaRequest(sql=ql_sql, description=description)
        ql_model = self._api.update(
            workspace=self.workspace, query_lambda=self.name, body=request
        ).get('data')
        if tag:
            tag_request = CreateQueryLambdaTagRequest(
                version=ql_model.version, tag_name=tag
            )
            self._api.create_0(
                workspace=self.workspace,
                query_lambda=self.name,
                body=tag_request
            )
        return QueryLambdaVersion(self._api, ql_model)

    def tag(self, tag):
        """Applies a specified tag to this Query Lambda version. If this tag is currently
        applied to another version of this Query Lambda, it will be moved. If not, it will
        be created.

        Args:
            tag (str): Version tag that wil be applied to this version.

        Returns:
            QueryLambdaVersion: the current QueryLambdaVersion object
        """
        tag_request = CreateQueryLambdaTagRequest(
            version=self.version, tag_name=tag
        )
        ql_model = self._api.create_0(
            workspace=self.workspace, query_lambda=self.name, body=tag_request
        ).get('data').get('version')
        return QueryLambdaVersion(self._api, ql_model)

    def execute(self, parameters=None, **kwargs):
        """Execute this Query Lambda using the given parameters and
        return a Cursor object to iterate through the results.

        If the Query Lambda was created without any parameters
        then no parameters need to be specified.

        If the Query Lambda was created with 1 or more query parameters,
        then all of those parameters can be specified as input.

        If a query parameter was not specified and a default value was
        provided for that query parameter when that Query Lambda version was
        created, then the default value will be used to execute the query.

        If a required query parameter was not specified,
        then an InputError Exception will be raised.

        Args:
            parameters (ParamDict): a ParamDict instance with values bound
            for all required query parameters, which will be used to
            execute this Query Lambda.

        Returns:
            Cursor: returns a cursor that can fetch query results
        """
        all_params = None
        if parameters:
            if not isinstance(parameters, rockset.ParamDict):
                raise ValueError(
                    "Query parameters of type `{}` is not supported. "
                    "Please pass a valid rockset.ParamDict object as input.".
                    format(type(parameters))
                )
            all_params = []
            for param in parameters.sqlparams():
                all_params.append(QueryParameter(**param))
        request = ExecuteQueryLambdaRequest(parameters=all_params, **kwargs)
        # TODO TODO TODO -- turn this into a Cursor
        return self._api.execute_0(
            workspace=self.workspace,
            query_lambda=self.name,
            version=self.version,
            body=request,
        )

    def drop(self):
        """Deletes the Query Lambda along with the current and all previous
        versions. Beware, this will permanently delete the Query Lambda and
        will be unrecoverable.
        """
        return self._api.delete(self.workspace, self.name).get('data')
