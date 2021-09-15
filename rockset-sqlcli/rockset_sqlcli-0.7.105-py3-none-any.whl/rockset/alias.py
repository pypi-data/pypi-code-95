"""
Usage
-----
Aliases are references to Rockset collections. You can use an
alias name in your queries instead of the actual collection name.

Example
-------
::

    from rockset import Client, Q
    import time

    # connect securely to Rockset
    rs = Client()

    # create an alias
    alias = rs.Alias.create(
        'myFirstAlias',
        workspace='commons',
        collections=['commons._events'])


    # wait for the alias to be ready
    while not alias.collections:
        alias = self.rs.Alias.retrieve(
            'myFirstAlias', workspace='commons'
        )
        time.sleep(1)


    # create a Query Lambda
    qlambda = rs.QueryLambda.create(
        'myQueryLambda',
        query=Q('SELECT * FROM commons.myFirstAlias LIMIT 10'))

    # execute a Query Lambda
    results = qlambda.execute()
    print(results)

.. _Alias.create:

Create a new alias
-------------------------
Create a new alias using the Client_ object using::

    from rockset import Client
    rs = Client()

    alias = rs.Alias.create(
        'myFirstAlias',
        description='alias referencing collection _events in workspace commons',
        workspace='commons',
        collections=['commons._events'])

.. _Alias.list:

List all aliases
--------------------
List all aliases using the Client_ object using::

    from rockset import Client
    rs = Client()

    # list all aliases across all workspaces
    aliases = rs.Alias.list()

    # list all aliases in a workspace
    aliases = rs.Alias.list(workspace='commons')

.. _Alias.retrieve:

Retrieve an existing alias
--------------------
Retrieve an existing alias by workspace and alias name::

    from rockset import Client
    rs = Client()

    # retrieve an alias
    alias = rs.Alias.retrieve('myFirstAlias', workspace='commons')

    # retrieve collections referenced
    referenced = alias.collections

.. _Alias.resolve:

Fetch the collections referenced by an alias
--------------------
Fetch the collection objects referenced by an alias::

    from rockset import Client
    import time
    rs = Client()

    # create an alias
    alias = rs.Alias.create(
        'myFirstAlias',
        workspace='commons',
        collections=['commons._events'])

    # wait for the alias to be ready
    while not alias.collections:
        alias = self.rs.Alias.retrieve(
            'myFirstAlias', workspace='commons'
        )
        time.sleep(1)

    # fetch the _events collection
    events = alias.resolve()[0]

.. _Alias.update:

Update an alias
-------------------------
Update an alias to reference a new collection::

    from rockset import Client
    rs = Client()

    # create a new collection
    rs.Collection.create("my-new-collection")

    # retrieve an alias
    alias = rs.Alias.retrieve('myFirstAlias', workspace='commons')

    # update collection referenced
    alias.update(collections=['commons.my-new-collection'])

.. _Alias.drop:

Drop an alias
-------------------------
Use the ``drop()`` method to remove an alias permanently from Rockset.

.. note:: This is a permanent and non-recoverable operation. Beware.

::

    from rockset import Client
    rs = Client()

    alias = rs.Alias.retrieve('myFirstAlias', workspace='commons')
    alias.drop()


"""

from rockset.swagger_client.api import (AliasesApi)
from rockset.swagger_client.models import (
    CreateAliasRequest, UpdateAliasRequest
)
from rockset.collection import Collection

import rockset


class AliasClient(object):
    def __init__(self, client):
        self._api = AliasesApi(client)
        self._client = client

    def create(
        self,
        name,
        description=None,
        workspace="commons",
        collections=[],
        **kwargs
    ):

        # construct CreateAliasRequest
        request = CreateAliasRequest(
            name=name,
            description=description,
            workspace=workspace,
            collections=collections,
        )

        # issue create api call
        alias = self._api.create(workspace=workspace, body=request).get('data')
        return Alias(self._api, self._client, alias)

    def list(self, workspace=None):
        if workspace:
            # If workspace specified, list aliases in that workspace
            aliases = self._api.workspace(workspace).get('data')
        else:
            # Else list all aliases across all workspaces in the org
            aliases = self._api.list().get('data')
        return [Alias(self._api, self._client, alias) for alias in aliases]

    def retrieve(self, name, workspace='commons', **kwargs):
        alias = self._api.get(workspace=workspace, alias=name).get('data')
        return Alias(self._api, self._client, alias)


class Alias(rockset.swagger_client.models.Alias):
    def __init__(self, api, client, model):
        super(Alias, self).__init__(**model.to_dict())
        self._api = api
        self._client = client
        self._model = model

    def resolve(self):
        # For now, each alias can only reference one collection
        # Return an array of collections to ensure backwards compat.
        split = splitPath(self.collections[0])
        return [
            Collection.retrieve(
                split['name'],
                workspace=split['workspace'],
                client=self._client
            )
        ]

    def update(self, description=None, collections=[]):
        request = UpdateAliasRequest(
            description=description, collections=collections
        )
        alias = self._api.update(
            workspace=self.workspace, alias=self.name, body=request
        ).get('data')
        return Alias(self._api, self._client, alias)

    def drop(self):
        return self._api.delete(self.workspace, self.name).get('data')


def splitPath(path):
    parts = path.rsplit('.', 1)
    return {'workspace': parts[0], 'name': parts[1]}
