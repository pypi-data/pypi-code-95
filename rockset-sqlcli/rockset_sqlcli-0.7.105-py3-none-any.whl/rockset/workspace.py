"""
Usage
-----
Workspace objects repesents a container of other workspaces and
Rockset collections.

Example
-------
::

    from rockset import Client, Q, F

    # connect securely to Rockset
    rs = Client()

    # create a workspace
    rs.Workspace.create('marketing')

    # create a collection in the workspace
    user_events = rs.Collection.create('user_events', workspace='marketing')

.. _Workspace.create:

Create a new workspace
-----------------------
Creating a workspace using the Client_ object is as simple as
calling ``client.Workspace.create('my-new-workspace')``::

    from rockset import Client
    rs = Client()
    new_ws = rs.Workspace.create('my-new-workspace')

.. _Workspace.list:

List all workspaces
--------------------
List all workspaces using the Client_ object using::

    from rockset import Client
    rs = Client()
    workspaces = rs.Workspace.list()

.. _Workspace.retrieve:

Retrieve an existing workspace
-------------------------------
Retrieve a workspace to run various operations on that workspace::

    from rockset import Client
    rs = Client()
    marketing = rs.Workspace.retrieve('marketing')

.. _Workspace.drop:

Drop a workspace
-----------------
Use the ``drop()`` method to remove a workspace permanently from Rockset.

.. note:: This is a permanent and non-recoverable operation. Beware.

::

    from rockset import Client
    rs = Client()
    marketing = rs.Workspace.drop('marketing')

"""
from rockset.swagger_client.api import (WorkspacesApi)
from rockset.swagger_client.models import (CreateWorkspaceRequest)


class WorkspaceClient(object):
    def __init__(self, client):
        self._api = WorkspacesApi(client)

    def create(self, name, description=None, **kwargs):
        request = CreateWorkspaceRequest(
            name=name,
            description=(description if description else ''),
        )
        return self._api.create(body=request).get('data')

    def list(self):
        return self._api.list().get('data')

    def get(self, name=None, **kwargs):
        return self._api.get(name).get('data')

    def delete(self, name=None, **kwargs):
        return self._api.delete(name).get('data')

    def retrieve(self, name=None, **kwargs):
        return self.get(name)

    def drop(self, name=None, **kwargs):
        return self.delete(name)
