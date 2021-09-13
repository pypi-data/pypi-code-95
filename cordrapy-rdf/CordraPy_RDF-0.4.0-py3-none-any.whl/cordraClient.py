# Standard Library packages
from typing import Dict
import json
import os
from copy import deepcopy

# Local imports
from .utils import check_response, pretty_print_POST
from .cordraMethods import (
    create_object, 
    read_object, 
    read_payload_info, 
    read_payload, 
    update_object, 
    delete_object, 
    find_objects, 
    create_token, 
    read_token, 
    delete_token
)


class CordraClient:
    """
    Supports CRUD operations with a running Cordra instance allows access to the full 
    functionality of the Cordra REST API. This includes:
    * Authorization using user / password
    * Authorization using a secret key
    * Provide a token for subsequent authorization
    * Delete a token
    * Create a cordra object
    * Setting the ACL on a cordra object on create
    * Updating a cordra object
    * Updating a cordra object attribute
    * Updating a cordra object payload
    * Updating the ACL of a cordra object
    * Deleting a cordra object
    * Deleting a cordra object attribute
    * Deleting a cordra object payload
    * Querying cordra

    Attributes:
        host: the location of the cordra instance (URL).
        credentials_file: the location of a user's credentials.

    >>> import cordra
    >>> test_object = cordra.CordraInstance("testhost")
    >>> print(test_object)
    Connection via CordraPy to testhost
    """

    host: str #URL
    handle: str
    credentials_file: str #FilePath
    params: Dict=dict()


    def __str__(self): 
        return f"Connection via CordraPy to {self.host}"


    def __init__(self, **params):
        assert "host" in params, "Host must be specified to use CordraClient"
        self.params.update(params)
        
        if "credentials_file" in params:
            self.get_auth(os.path.expanduser(params["credentials_file"]))

            self.schemas = {
                r.get("name"): r.get("schema")
                for r in self.find("type:Schema")['results']
            }


    def get_auth(self, credentials_file):
        """Get a token with credentials"""

        # Open loginfile and check it is valid
        with open( credentials_file ) as f:
            login = json.load(f)
        assert login.keys() == {"username","password"}

        login.update(self.params)

        r = create_token(**login)

        # Set up variables and default auth for future requests
        self.params["token"] = r["access_token"]


    def check_auth(self):
        """Checks an access Token"""
        r = read_token(**self.params)
        return r


    def delete_auth(self):
        """Delete an access Token"""
        r = delete_token(**self.params)
        return r


    def create(self, obj, obj_type, **kwargs):
        """Creates an object"""

        params = deepcopy(self.params)
        params.update(kwargs)

        return create_object(obj_json=obj, obj_type=obj_type, **params)


    def read(self, obj_id, getAll=False, **kwargs):
        """Retrieve an object from Cordra by identifer and create a
        python CordraObject."""

        params = deepcopy(self.params)
        params.update(kwargs)

        if getAll:
            params["full"] = True

        obj = read_object(obj_id=obj_id, **params)

        if getAll and "payloads" in obj:
            payload_info = deepcopy( obj["payloads"] )
            obj["payloads"] = dict()
            payload_info = read_payload_info(obj_id=obj_id, **params)

            for pay in payload_info:
                payName = pay.get("name")
                obj["payloads"][payName] = read_payload(obj_id=obj_id, payload=payName, **params)

        return obj


    def update(self, obj, obj_id, **kwargs):
        """Updates an object"""

        params = deepcopy(self.params)
        params.update(kwargs)

        return update_object(obj_id=obj_id, obj_json=obj, **params)


    def delete(self, obj_id, **kwargs):
        """Delete a Cordra object or part of a Cordra Object"""

        params = deepcopy(self.params)
        params.update(kwargs)

        return delete_object(obj_id=obj_id, **params)


    def find(self, query, **kwargs):
        """Find a Cordra object by query"""

        params = deepcopy(self.params)
        params.update(kwargs)

        return find_objects(query=query, **params)
