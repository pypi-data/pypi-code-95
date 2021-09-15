"""
Usage
-----
Collection objects repesents a single Rockset collection.
These objects are generally created using a Rockset Client_
object using methods such as::

    from rockset import Client

    # connect to Rockset
    rs = Client()

    # create a new collection
    user_events = rs.Collection.create('user-events')

    # retrieve an existing collection
    users = rs.Collection.retrieve('users')

You can add documents to the collection using the ``add_docs()`` method. Each
document in a collection is uniquely identified by its ``_id`` field.

If documents added have ``_id`` fields that match existing documents,
then their contents will be merged. Otherwise, the new documents will be
added to the collection.

You can remove documents from a collection using the ``remove_docs()`` method.

Refer to the Query_ module for documentation and examples on how to query
collections.

Example
-------
::

    from rockset import Client, Q, F

    # connect securely to Rockset
    rs = Client()

    # retrieve the relevant collection
    emails = rs.Collection.retrieve('emails')

    # look for all emails to johndoe that contains the term 'secret'
    johndoe_secret_q = Q('emails').where(
        (F["to"].startswith('johndoe@')) & (F["body"][:] == 'secret')
    )

    # query the collection
    docs = rs.sql(johndoe_secret_q).results()

.. _Collection.create:

Create a new collection
-----------------------
Creating a collection using the Client_ object is as simple as
calling ``client.Collection.create("my-new-collection")``::

    from rockset import Client
    rs = Client()
    new_collection = rs.Collection.create("my-new-collection")

    # create a collection in a workspace
    leads_collection = rs.Collection.create("leads",
                                            workspace="marketing")

    # create a collection and map timestamp field to event-time
    field_mappings = [
      rs.FieldMapping.mapping(
        name="transformation1",
        input_fields=[
          rs.FieldMapping.input_field(
            field_name="ts",
              if_missing="PASS",
              is_drop=True,
              param="ts"
          )
        ],
        output_field=rs.FieldMapping.output_field(
            field_name="_event_time",
            sql_expression="CAST(:ts AS TIMESTAMP)",
            on_error="SKIP"
        )
      )
    ]

    event_data_collection = rs.Collection.create("event-data-collection",
                                                 field_mappings=field_mappings)

Creating a collection with a retention duration of 10 days::

    from rockset import Client
    rs = Client()
    new_collection_with_retention = rs.Collection.create("my-event-collection",
                                                         retention_secs=10*24*60*60)

.. _Collection.list:

List all collections
--------------------
List all collections using the Client_ object using::

    from rockset import Client
    rs = Client()

    # list all collections
    collections = rs.Collection.list()

.. _Collection.retrieve:

Retrieve an existing collection
-------------------------------
Retrive a collection to run various operations on that collection
such as adding or removing documents or executing queries::

    from rockset import Client
    rs = Client()
    users = rs.Collection.retrieve('users')

    # retrieve a collection in a workspace
    users = rs.Collection.retrieve('users', workspace='marketing')


.. _Collection.describe:

Describe an existing collection
-------------------------------
The ``describe`` method can be used to fetch all the details about the collection
such as what data sets act as the collection's sources, various performance and
usage statistics::

    from rockset import Client
    rs = Client()
    users = rs.Collection.retrieve('users')
    print(users.describe())

.. _Collection.drop:

Drop a collection
-----------------
Use the ``drop()`` method to remove a collection permanently from Rockset.

.. note:: This is a permanent and non-recoverable operation. Beware.

::

    from rockset import Client
    rs = Client()
    users = rs.Collection.retrieve('users')
    users.drop()

.. _Collection.add_docs:

Add documents to a collection
-----------------------------
Python dicts can be added as documents to a collection using the ``add_docs``
method. Documents are uniquely identified by the ``_id`` field. If an input
document does not have an ``_id`` field, then an unique id will be assigned
by Rockset.

If the ``_id`` field of an input document does not match an existing document,
then a new document will be created.

If the ``_id`` field of an input document matches an existing document,
then the new document will be merged with the existing document::

    from rockset import Client
    import json

    rs = Client()
    with open('my-json-array-of-dicts.json') as data_fh:
        ret = rs.Collection.add_docs('users', json.load(data_fh))

.. _Collection.remove_docs:

Delete documents from a collection
----------------------------------
Remove documents from a collection using the ``remove_docs`` method::

    from rockset import Client

    rs = Client()
    users_to_remove = ['user007', 'user042', 'user435']
    docs_to_remove = [{'_id': u} for u in users_to_remove]
    ret = rs.Collection.remove_docs('users', docs_to_remove)

"""
from .exception import InputError
from .resource import Resource

from rockset.swagger_client.api import (CollectionsApi, DocumentsApi)
from rockset.swagger_client.models import (
    CreateCollectionRequest, AddDocumentsRequest, PatchDocumentsRequest,
    DeleteDocumentsRequest
)


class Collection(Resource):
    """
    Collection objects represent a single Rockset collection.

    Objects of this class are never instantiated directly and are
    generally returned by methods such as::

        from rockset import Client
        rs = Client()
        first = rs.Collection.create('my-first-collection')
        another = rs.Collection.retrieve('another-collection')

    See more examples and documentation here.
    """
    @classmethod
    def create(
        cls,
        name,
        workspace="commons",
        description=None,
        sources=None,
        retention_secs=None,
        field_mappings=None,
        clustering_key=None,
        **kwargs
    ):
        """Creates a new Rockset collection.

        Use it via rockset.Client().Collection.create()

        Only alphanumeric characters, ``_``, and ``-`` are allowed
        in collection names.

        Args:
            name (str): name of the collection to be created.
            description (str): a human readable description of the collection
            sources (Source): array of Source objects that defines the set
                of input data sources for this collection
            retention_secs (int): an integer representing minimum duration (in seconds),
                for which documents are retained in this collection before being automatically deleted.
            field_mappings (FieldMapping): array of FieldMapping objects that
                defines the set of transformations to apply on all documents
            clustering_key (ClusteringKey): array of ClusteringKey objects
                that defines the clustering config for this collection
        Returns:
            Collection: Collection object
        """
        if 'client' not in kwargs:
            raise ValueError(
                'incorrect API usage. '
                'use rockset.Client().Collection.create() instead.'
            )
        client = kwargs.pop('client')

        kwargs['description'] = description
        kwargs['sources'] = sources
        kwargs['retention_secs'] = retention_secs
        kwargs['field_mappings'] = field_mappings
        kwargs['clustering_key'] = clustering_key

        req = CreateCollectionRequest(name=name, **kwargs)
        collection = CollectionsApi(client).create(
            workspace=workspace, body=req
        ).get('data').to_dict()

        return cls(client=client, **collection)

    @classmethod
    def retrieve(cls, name, **kwargs):
        """Retrieves details of a single collection

        Use it via rockset.Client().Collection.retrieve()

        Args:
            name (str): Name of the collection

        Returns:
            Collection: Collection object
        """
        if 'client' not in kwargs:
            raise ValueError(
                'incorrect API usage. '
                'use rockset.Client().Collection.create() instead.'
            )
        c = cls(name=name, **kwargs)
        c.describe()

        return c

    @classmethod
    def list(cls, **kwargs):
        """Returns list of all collections.

        Use it via rockset.Client().Collection.list()

        Returns:
            List: A list of Collection objects
        """
        if 'client' not in kwargs:
            raise ValueError(
                'incorrect API usage. '
                'use rockset.Client().Collection.list() instead.'
            )
        client = kwargs.pop('client')
        workspace = kwargs.pop('workspace', None)
        capi = CollectionsApi(client)

        if workspace:
            collections = capi.workspace(workspace).get('data')
        else:
            collections = capi.list().get('data')

        ret = []
        for c in collections:
            if isinstance(c, dict):
                c_dict = c
            else:
                c_dict = c.to_dict()

            ret.append(cls(client=client, **c_dict))

        return ret

    def __init__(self, *args, **kwargs):
        kwargs['type'] = 'COLLECTION'
        super(Collection, self).__init__(*args, **kwargs)
        self.docs_per_call = 1000

    def _chopper(self, docs):
        return [
            docs[i:i + self.docs_per_call]
            for i in range(0, len(docs), self.docs_per_call)
        ]

    def _validate_doclist(self, docs, action):
        if type(docs) != list:
            raise InputError(message='arg "docs" is not a list of dicts')
        for doc in docs:
            if not isinstance(doc, dict):
                raise InputError(
                    message=
                    f'cannot {action} a document that is not a dict or rockset.Document'
                )

    # instance methods
    def describe(self):
        """Returns all properties of the collection as a dict.

        Returns:
            dict: properties of the collection
        """
        return super(Collection, self).describe()

    def drop(self):
        """Deletes the collection represented by this object.

        If successful, the current object will contain
        a property named ``dropped`` with value ``True``

        Example::

            ...
            print(my_coll.asdict())
            my_coll.drop()
            print(my_coll.dropped)       # will print True
            ...
        """
        super(Collection, self).drop()
        return

    def query(self, q, timeout=None, flood_all_leaves=False):
        return super(Collection, self).query(
            q, timeout=timeout, flood_all_leaves=flood_all_leaves
        )

    def setstate(self, newstate):
        return super(Collection, self).setstate(newstate)

    def add_docs(self, docs, timeout=None):
        """Adds or merges documents to the collection. Provides document
        level atomicity.

        Documents within a collection are uniquely identified by the
        ``_id`` field. If input document does not specify ``_id``, then
        an unique UUID will be assigned to the document.

        If the ``_id`` field of an input document does not match with
        any existing collection documents, then the input document will
        be inserted.

        If the ``_id`` field of an input document matches with an
        existing collection document, then the input document will be
        merged atomically as described below:

        * All fields present in both the input document and the collection
          document will be updated to values from the input document.
        * Fields present in the input document but not the collection
          document will be inserted.
        * Fields present in the collection document but not the input
          document will be left untouched.

        All fields within every input document will be inserted or updated
        atomically. No atomicity guarantees are provided across two different
        documents added.

        Example::

            from rockset import Client

            rs = Client()
            docs = [
                {"_id": "u42", "name": {"first": "Jim", "last": "Gray"}},
                {"_id": "u1201", "name": {"first": "David", "last": "DeWitt"}},
            ]
            results = rs.Collection.add_docs("my-favorite-collection", docs)
            ...

        Args:
            name (str): Name of the collection
            docs (list of dicts): New documents to be added or merged
            timeout (int): Client side timeout. When specified,
                RequestTimeout_ exception will
                be thrown upon timeout expiration. By default, the client
                will wait indefinitely until it receives results or an
                error from the server.

        Returns:
            Dict: The response dict will have 1 field: ``data``

            The ``data`` field will be a list of document status records,
            one for each input document indexed in the same order as the list
            of input documents provided as part of the request. Each of those
            document status records will have fields such as the document
            ``_id``, ``_collection`` name, ``status`` describing if that
            particular document add request succeeded or not, and an optional
            ``error`` field with more details.
        """
        self._validate_doclist(docs, 'add')

        # chunk docs to operate in batches
        retval = []
        for chunk in self._chopper(docs):
            request = AddDocumentsRequest(data=chunk)
            retval.extend(
                DocumentsApi(self.client).add(
                    workspace=self.workspace,
                    collection=self.name,
                    body=request,
                    _request_timeout=timeout
                ).get('data')
            )
        return retval

    def patch_docs(self, docpatches, timeout=None):
        """Updates documents in the collection.

        This method expects a list of docpatches, where each docpatch
        describes a set of updates that need to be applied to a single
        document in the collection.

        All updates specified in a single docpatch will be applied atomically
        to the document. If a single patch operation specified in a patch
        fails, the entire patch operation will be aborted.

        Each docpatch is a dict that is required to have 2 fields\:

        1. ``_id`` that holds the _id field of the document to be updated

        2. ``patch`` that holds a list of patch operations to be applied
           to that document, following the JSONPatch standard defined at
           http://jsonpatch.com

        Example::

            from rockset import Client
            rs = Client()

            docpatch = {
                "_id": "u42",
                "patch": [
                    {"op": "replace", "path": "/name/middle", "value": "Nicholas"}
                ]
            }
            rs.Collection.patch_docs('my-collection', [docpatch])

        Each patch is a list of individual patch operations, where each patch
        operation specifies how a particular field or field path within the
        target document should be updated.

        Each patch operation is a dict with a key called "op" (for
        operation) and few more keys that act as arguments to the "op", which
        differ from one operation type to another. The JSONPatch standard
        defines several types of patch operations, their arguments and their
        behavior. Refer to http://jsonpatch.com/#operations for more details.

        If a patch opertion's argument is a field path, then it is specified
        using the JSON Pointer standard defined at https://tools.ietf.org/html/rfc6901
        In essence, field paths are represented as a string of tokens
        separated by ``/`` characters. These tokens either specify keys in
        objects or indexes into arrays, and arrays are 0-based.

        For example, in this document::

            {
                "biscuits": [
                    { "name": "Digestive" },
                    { "name": "Choco Leibniz" }
                ]
            }

            "/biscuits" would point to the array of biscuits
            "/biscuits/1/name" would point to "Choco Leibniz".


        Here are some examples of individual patch operations:

        * Add

          Example::

              { "op": "add", "path": "/biscuits/1", "value": { "name": "Ginger Nut" } }

          Adds a value to an object or inserts it into an array. In the
          case of an array, the value is inserted before the given index.
          The ``-`` character can be used instead of an index to insert at the
          end of an array.

        * Remove

          Example::

              { "op": "remove", "path": "/biscuits" }

          Removes a value from an object or array.

          Another Example::

              { "op": "remove", "path": "/biscuits/0" }

          Removes the first element of the array at biscuits
          (or just removes the "0" key if biscuits is an object)

        * Replace

          Example::

              { "op": "replace", "path": "/biscuits/0/name", "value": "Chocolate Digestive" }

          Replaces a value. Equivalent to a "remove" followed by an "add".

        * Copy

          Example::

              { "op": "copy", "from": "/biscuits/0", "path": "/best_biscuit" }

          Copies a value from one location to another within the JSON document.
          Both "from" and "path" are JSON Pointers.

        * Move

          Example::

              { "op": "move", "from": "/biscuits", "path": "/cookies" }

          Moves a value from one location to the other. Both "from" and "path" are
          JSON Pointers.

        * Test

          Example::

              { "op": "test", "path": "/best_biscuit/name", "value": "Choco Leibniz" }

          Tests that the specified value is set in the document. If the test
          fails, then the patch as a whole will not apply.

        Args:
            name (str): Name of the collection
            docpatches (list of dicts): List of document patches to be applied.
            timeout (int): Client side timeout. When specified,
                RequestTimeout_ exception will
                be thrown upon timeout expiration. By default, the client
                will wait indefinitely until it receives results or an
                error from the server.

        Returns:
            Dict: The response dict will have 1 field: ``data``.

            The ``data`` field will be a list of document status records,
            one for each input document indexed in the same order as the list
            of input documents provided as part of the request. Each of those
            document status records will have fields such as the document
            ``_id``, ``_collection`` name, ``status`` describing if that
            particular document add request succeeded or not, and an optional
            ``error`` field with more details.
        """
        self._validate_doclist(docpatches, 'patch')

        # chunk docs to operate in batches
        retval = []
        for chunk in self._chopper(docpatches):
            request = PatchDocumentsRequest(data=chunk)
            retval.extend(
                DocumentsApi(self.client).patch(
                    workspace=self.workspace,
                    collection=self.name,
                    body=request,
                    _request_timeout=timeout
                ).get('data')
            )
        return retval

    def remove_docs(self, docs, timeout=None):
        """Deletes documents from the collection. The ``_id`` field needs to
        be populated in each input document. Other fields in each document
        will be ignored.

        Args:
            name (str): Name of the collection
            docs (list of dicts): Documents to be deleted.
            timeout (int): Client side timeout. When specified,
                RequestTimeout_ exception will
                be thrown upon timeout expiration. By default, the client
                will wait indefinitely until it receives results or an
                error from the server.

        Returns:
            Dict: The response dict will have 1 field: ``data``.

            The ``data`` field will be a list of document status records,
            one for each input document indexed in the same order as the list
            of input documents provided as part of the request. Each of those
            document status records will have fields such as the document
            ``_id``, ``_collection`` name, ``status`` describing if that
            particular document add request succeeded or not, and an optional
            ``error`` field with more details.
        """
        self._validate_doclist(docs, 'remove')

        # chunk docs to operate in batches
        retval = []
        docids = [{'_id': doc.get('_id', None)} for doc in docs]
        for chunk in self._chopper(docids):
            request = DeleteDocumentsRequest(data=chunk)
            retval.extend(
                DocumentsApi(self.client).delete(
                    workspace=self.workspace,
                    collection=self.name,
                    body=request,
                    _request_timeout=timeout
                ).get('data')
            )
        return retval


__all__ = [
    'Collection',
]
