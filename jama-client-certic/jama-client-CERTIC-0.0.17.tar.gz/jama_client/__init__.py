"""
# Jama client library

## Installation

Use pip to install:

    pip install jama-client-CERTIC

## Quick start

    from jama_client import Client
    client = Client("https://acme.tld/rpc/", "secretapikeyhere")
    file_id = client.upload("/path/to/some/file.jpg")
    collection_id = client.add_collection("title of the collection")
    client.add_file_to_collection(file_id, collection_id)


"""
import os
import math
import hashlib
from requests import post
from typing import Any, Union, List, Dict, Optional
import base64


DEFAULT_UPLOAD_CHUNK_SIZE = 1024 * 1024


def _file_hash256(file_path: str) -> str:
    hsh = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chnk in iter(lambda: f.read(8192), b""):
            hsh.update(chnk)
    return hsh.hexdigest()


def _get_nb_of_chunks(
    file_path: str, chunk_size: int = DEFAULT_UPLOAD_CHUNK_SIZE
) -> int:
    size = os.path.getsize(file_path)
    return math.ceil(size / chunk_size)


def _get_file_slice(
    file_path: str, from_byte: int, max_size: int = DEFAULT_UPLOAD_CHUNK_SIZE
) -> bytes:
    with open(file_path, "rb") as f:
        f.seek(from_byte)
        return f.read(max_size)


class IncompleteUpload(RuntimeError):
    pass


class AlreadyUploaded(RuntimeError):
    pass


class ServiceError(RuntimeError):
    def __init__(self, message):
        super(ServiceError, self).__init__()
        self.message = message


class _Method(object):
    def __init__(self, send, name):
        self.__send = send
        self.__name = name

    def __getattr__(self, name):
        return _Method(self.__send, "{}.{}".format(self.__name, name))

    def __call__(self, *args):
        return self.__send(self.__name, args)


class _Chunker:
    def __init__(self, file_path: str, chunk_size: int = DEFAULT_UPLOAD_CHUNK_SIZE):
        self._file_path = file_path
        self._chunk_size = chunk_size
        self.nb_of_chunks = _get_nb_of_chunks(self._file_path, self._chunk_size)
        self.file_hash = _file_hash256(self._file_path)

    def get_chunk(self, number_of_chunk) -> bytes:
        if number_of_chunk > self.nb_of_chunks or number_of_chunk < 0:
            raise ValueError("Chunk number out of range")
        return _get_file_slice(
            self._file_path, self._chunk_size * number_of_chunk, self._chunk_size
        )

    @property
    def chunks(self):
        for i in range(self.nb_of_chunks):
            yield self.get_chunk(i)


class _ChunksUploader:
    def __init__(
        self,
        file_path: str,
        endpoint: str,
        api_key: str,
        chunk_size: int = DEFAULT_UPLOAD_CHUNK_SIZE,
        file_name: str = None,
        origin_dir_name: str = None,
    ):
        self.foreign_reference = None
        self._file_path = file_path
        self._file_name = file_name
        self._origin_dir_name = origin_dir_name
        self._api_key = api_key
        self._endpoint = endpoint
        self._chunker = _Chunker(file_path, chunk_size)
        self.chunks_statuses = {}
        for i in range(self.number_of_chunks):
            self.chunks_statuses[i] = {
                "chunk_number": i,
                "tries": 0,
                "done": False,
                "message": "",
            }

    @property
    def number_of_chunks(self) -> int:
        return self._chunker.nb_of_chunks

    @property
    def is_complete(self) -> bool:
        for k in self.chunks_statuses:
            if not self.chunks_statuses[k]["done"]:
                return False
        return True

    def upload_all(self):
        if self.foreign_reference is None:
            for i in range(self.number_of_chunks):
                if not self.chunks_statuses[i]["done"]:
                    self.upload(i)

    def upload(self, chunk_number: int):
        self.chunks_statuses[chunk_number]["tries"] = (
            self.chunks_statuses[chunk_number]["tries"] + 1
        )
        try:
            headers = {
                "X-Api-Key": self._api_key,
                "X-file-chunk": "{}/{}".format(chunk_number, self.number_of_chunks),
                "X-file-hash": self._chunker.file_hash,
                "X-file-name": base64.b64encode(
                    (self._file_name or os.path.basename(self._file_path)).encode(
                        "utf-8"
                    )
                ),
            }
            if self._origin_dir_name:
                headers["X-origin-dir"] = self._origin_dir_name
            response = post(
                url=self._endpoint,
                data=self._chunker.get_chunk(chunk_number),
                headers=headers,
            )
            if response.status_code == 202:
                self.chunks_statuses[chunk_number]["done"] = True
            elif response.status_code == 200:
                for i in range(self.number_of_chunks):
                    self.chunks_statuses[i]["done"] = True
                self.foreign_reference = int(response.text)
            else:
                self.chunks_statuses[chunk_number][
                    "message"
                ] = "failed with status {} {}".format(
                    response.status_code, response.text
                )
        except Exception as e:
            self.chunks_statuses[chunk_number]["message"] = getattr(
                e, "message", repr(e)
            )


class Client:
    def __init__(self, endpoint: str, api_key: str):
        self._endpoint = endpoint
        self._api_key = api_key
        self.requests_count = 0
        self.upload_status = {}

    def __getattr__(self, name):
        return _Method(self.__call, name)

    def __call(self, method: str, params: List = None) -> Any:
        self.requests_count = self.requests_count + 1
        payload = {"method": method, "params": params or [], "id": self.requests_count}
        try:
            response = post(
                url=self._endpoint, json=payload, headers={"X-Api-Key": self._api_key}
            )
        except Exception:
            raise ServiceError("Could not contact service")
        if response.status_code == 200:
            message = response.json()
            if message["error"] is None:
                return message["result"]
            else:
                raise ServiceError(message["error"])
        else:
            raise ServiceError(
                "Response ended with status code {}".format(response.status_code)
            )

    def upload(
        self,
        file_path: str,
        chunk_size: int = DEFAULT_UPLOAD_CHUNK_SIZE,
        file_name: str = None,
        origin_dir_name: str = None,
    ) -> int:
        """
        This methods uploads a file in multiple chunks, allowing
        resumable uploads.

        ```file_path``` is the local path to the file.

        ```chunk_size``` is the number of bytes uploaded with each chunk of the file.

        ```file_name``` overides the name of the file, should you want a different name in Jama than
        the local name.

        ```origin_dir_name``` is a directory path (```dirA/dirB/dirC```). This path triggers
        the creation of the corresponding collections and sub-collections in Jama.
        """
        upload_infos = self.upload_infos(_file_hash256(file_path))
        if upload_infos.get("status") == "available":
            raise AlreadyUploaded()

        chunked_upload = _ChunksUploader(
            file_path,
            self._endpoint + "upload/partial/",
            self._api_key,
            chunk_size,
            file_name,
            origin_dir_name,
        )

        # Resume upload across sessions
        # Set chunk status to "done" if already available
        # on the server
        if upload_infos.get("status") == "incomplete":
            for available_chunk in upload_infos.get("available_chunks", []):
                _, chunk_number = os.path.splitext(available_chunk)[0].split("-")
                chunk_number = int(chunk_number.lstrip("0") or "0")
                chunked_upload.chunks_statuses[chunk_number]["done"] = True

        chunked_upload.upload_all()
        if not chunked_upload.is_complete:
            self.upload_status[file_path] = chunked_upload.chunks_statuses
            # If incomplete, raise exception so the
            # client can decide to retry or not.
            raise IncompleteUpload()
        return chunked_upload.foreign_reference

    def activate_rpc_access(self, user_name: str, api_key: str) -> bool:
        """
        Add access to the RPC API for the given user name with the given API key.
        A new user will be created if none is available with given user name.

        Note: only user with admin privileges can use this.
        """
        return self.__call("activate_rpc_access", [user_name, api_key])

    def add_collection(self, title: str, parent_id: int = None) -> Optional[Dict]:
        """
        Create a new collection based on 'title'. If 'parent_id' is set,
        will create new collection as child of parent. Otherwise, the new
        collection is created at root.

        Returns either the serialized new collection of null if parent does
        not exist.

        Example output:

        ```
        {
            "id": 3,
            "title": "paintings",
            "resources_count": 0,
            "children_count": 0,
            "descendants_count": 0,
            "descendants_resources_count": 0,
            "parent": null,
            "children": null,
            "metas": [],
            "public_access": false,
            "tags": [],
        }
        ```
        """
        return self.__call("add_collection", [title, parent_id])

    def add_collection_from_path(self, path: str) -> List[Dict]:
        """
        Will take a path such as '/photos/arts/paintings/'
        and build the corresponding hierarchy of collections. The hierarchy
        is returned as a list of serialized collections.

        Beware: Because the collections are serialized before their children,
        all the children/descendants counts are set to 0.

        Example output:

        ```
        [
            {
                "id": 1,
                "title": "photos",
                "resources_count": 0,
                "children_count": 0,
                "descendants_count": 0,
                "descendants_resources_count": 0,
                "parent": null,
                "children": null,
                "metas": [],
                "public_access": false,
                "tags": [],
            },
            {
                "id": 2,
                "title": "arts",
                "resources_count": 0,
                "children_count": 0,
                "descendants_count": 0,
                "descendants_resources_count": 0,
                "parent": 1,
                "children": null,
                "metas": [],
                "public_access": false,
                "tags": [],
            },
            {
                "id": 3,
                "title": "paintings",
                "resources_count": 0,
                "children_count": 0,
                "descendants_count": 0,
                "descendants_resources_count": 0,
                "parent": 2,
                "children": null,
                "metas": [],
                "public_access": false,
                "tags": [],
            },
        ]
        ```
        """
        return self.__call("add_collection_from_path", [path])

    def add_meta_to_collection(
        self, collection_id: int, meta_id: int, meta_value: str
    ) -> Union[int, bool]:
        """
        Add a meta value to a collection given their ids.
        """
        return self.__call(
            "add_meta_to_collection", [collection_id, meta_id, meta_value]
        )

    def add_meta_to_resource(
        self, resource_id: int, meta_id: int, meta_value: str
    ) -> Union[int, bool]:
        """
        Add a meta value to a resource given their ids.
        """
        return self.__call("add_meta_to_resource", [resource_id, meta_id, meta_value])

    def add_metadata(
        self, title: str, metas_set_id: int, metadata_type_id: int = None
    ) -> Union[int, bool]:
        """
        Add a new metadata to metadata set.

        Set optional 'metadata_type_id'
        """
        return self.__call("add_metadata", [title, metas_set_id, metadata_type_id])

    def add_metadataset(self, title: str) -> int:
        """
        Create new metadata set from title.
        """
        return self.__call("add_metadataset", [title])

    def add_resource_to_collection(self, resource_id: int, collection_id: int) -> bool:
        """
        Add a resource to a collection given ids.
        """
        return self.__call("add_resource_to_collection", [resource_id, collection_id])

    def add_tag_to_collection(self, tag_uid: str, collection_id: int) -> bool:
        """
        Add tag to a collection based on tag uid and collection id.
        """
        return self.__call("add_tag_to_collection", [tag_uid, collection_id])

    def add_tag_to_resource(self, tag_uid: str, resource_id: int) -> bool:
        """
        Add tag to a resource based on tag uid and resource id.
        """
        return self.__call("add_tag_to_resource", [tag_uid, resource_id])

    def advanced_search(self, search_terms: List[Dict]) -> Dict[str, List]:
        """
        Performs a complex search using terms such as 'contains', 'is', 'does_not_contain'.

        Multiple conditions can be added.

        Example input:

        ```
        [
            {"property": "title", "term": "contains", "value": "cherbourg"},
            {"meta": 123, "term": "is", "value": "35mm"},
            {"tags": ["PAINTINGS", "PHOTOS"]}
        ]
        ```

        Example output:

        ```
        {
            "collections": [],
            "resources": [
                {
                "id": 1,
                "title": "Cherbourg by night",
                "original_name": "cherbourg_by_night.jpg",
                "type": "image/jpeg",
                "hash": "0dd93a59aeaccfb6d35b1ff5a49bde1196aa90dfef02892f9aa2ef4087d8738e",
                "metas": null,
                "urls": [],
                "tags": [],
                }
            ]
        }
        ```
        """
        return self.__call("advanced_search", [search_terms])

    def advanced_search_terms(self) -> List[str]:
        """
        Return terms conditions to be used in advanced search.

        Example output:

        ```
        [
            "is",
            "contains",
            "does_not_contain"
        ]
        ```
        """
        return self.__call("advanced_search_terms", [])

    def ancestors_from_collection(
        self, collection_id: int, include_self: bool = False
    ) -> List[dict]:
        """
        Get ancestors from collection id as a list of serialized collections.

        If 'include_self' is true, will add the current collection at the begining.

        Example output:

        ```
        [
            {
                "id": 1,
                "title": "photos",
                "resources_count": 0,
                "children_count": 0,
                "descendants_count": 0,
                "descendants_resources_count": 0,
                "parent": null,
                "children": null,
                "metas": [],
                "public_access": false,
                "tags": [],
            },
            {
                "id": 2,
                "title": "arts",
                "resources_count": 0,
                "children_count": 0,
                "descendants_count": 0,
                "descendants_resources_count": 0,
                "parent": 1,
                "children": null,
                "metas": [],
                "public_access": false,
                "tags": [],
            },
            {
                "id": 3,
                "title": "paintings",
                "resources_count": 0,
                "children_count": 0,
                "descendants_count": 0,
                "descendants_resources_count": 0,
                "parent": 2,
                "children": null,
                "metas": [],
                "public_access": false,
                "tags": [],
            },
        ]
        ```
        """
        return self.__call("ancestors_from_collection", [collection_id, include_self])

    def ancestors_from_resource(self, resource_id: int) -> List[List[dict]]:
        """
        Get ancestors from resource id as a list of serialized collections.

        Example output:

        ```
        [
            {
                "id": 1,
                "title": "photos",
                "resources_count": 0,
                "children_count": 0,
                "descendants_count": 0,
                "descendants_resources_count": 0,
                "parent": null,
                "children": null,
                "metas": [],
                "public_access": false,
                "tags": [],
            },
            {
                "id": 2,
                "title": "arts",
                "resources_count": 0,
                "children_count": 0,
                "descendants_count": 0,
                "descendants_resources_count": 0,
                "parent": 1,
                "children": null,
                "metas": [],
                "public_access": false,
                "tags": [],
            },
            {
                "id": 3,
                "title": "paintings",
                "resources_count": 0,
                "children_count": 0,
                "descendants_count": 0,
                "descendants_resources_count": 0,
                "parent": 2,
                "children": null,
                "metas": [],
                "public_access": false,
                "tags": [],
            },
        ]
        ```
        """
        return self.__call("ancestors_from_resource", [resource_id])

    def change_collection_meta_value(self, meta_value_id: int, meta_value: str) -> bool:
        """
        Change the value of a meta for a collection.
        """
        return self.__call("change_collection_meta_value", [meta_value_id, meta_value])

    def change_resource_meta_value(self, meta_value_id: int, meta_value: str) -> bool:
        """
        Change the value of a meta for a resource
        """
        return self.__call("change_resource_meta_value", [meta_value_id, meta_value])

    def collection(self, collection_id: int = None) -> Optional[Dict]:
        """
        Get a particular collection given its id.

        Example output:

        ```
        {
            "id": 2,
            "title": "art works",
            "resources_count": 23,
            "children_count": 5,
            "descendants_count": 12,
            "descendants_resources_count": 58,
            "parent": 1,
            "children": None,
            "metas": [],
            "public_access": False,
            "tags": [],
        }
        ```

        if collection id is null, will only return the number of collections at root:

        ```
        {
            "id": None,
            "title": "root",
            "children_count": 25,
        }
        ```
        """
        return self.__call("collection", [collection_id])

    def collections(
        self,
        parent_id: int = None,
        recursive: bool = False,
        limit_from: int = 0,
        limit_to: int = 2000,
        flat_list: bool = False,
        only_published: bool = False,
    ) -> List[Dict]:
        """
        Return the user's collections under the parent collection
        specified by 'parent_id'. If 'parent_id' is null, will return
        collections available at root. If 'recursive' is true, will
        return all the descendants recursively in the 'children' key.
        If recursive is false, 'children' is null.

        Example output:

        ```
        [
            {
                "id": 2,
                "title": "art works",
                "resources_count": 23,
                "children_count": 5,
                "descendants_count": 12,
                "descendants_resources_count": 58,
                "parent": 1,
                "children": None,
                "metas": [],
                "public_access": False,
                "tags": [],
            }
        ]
        ```
        """
        return self.__call(
            "collections",
            [parent_id, recursive, limit_from, limit_to, flat_list, only_published],
        )

    def deactivate_rpc_access(self, user_name: str, api_key: str) -> bool:
        """
        Deactivate access to the RPC API for the given user name and API key.
        Only the access (API key) is removed, not the user.

        Note: only user with admin privileges can use this.
        """
        return self.__call("deactivate_rpc_access", [user_name, api_key])

    def delete_collection(self, collection_id: int, recursive: bool = False) -> Dict:
        """
        Delete collection given its id.

        Collection MUST be empty of any content (no children collections and no resources),
        unless the 'recursive'parameter is set to True.
        """
        return self.__call("delete_collection", [collection_id, recursive])

    def delete_metadata(self, metadata_id: int) -> bool:
        """
        Delete metadata based on its id.
        """
        return self.__call("delete_metadata", [metadata_id])

    def delete_metadataset(self, metadataset_id: int, recursive: bool = False) -> Dict:
        """
        Delete metadata set based on its id. Optional recursive
        call.
        """
        return self.__call("delete_metadataset", [metadataset_id, recursive])

    def delete_resource(self, resource_id: int) -> bool:
        """
        Permanently delete a resource given its id.
        """
        return self.__call("delete_resource", [resource_id])

    def metadata(self, metadata_id: int) -> Optional[Dict]:
        """
        Get one particular metadata given its id.

        Example output:

        ```
        {
            "id": 2,
            "title": "ICC_Profile:GrayTRC",
            "set_id": 1,
            "set_title": "exif metas",
            "rank": 1,
            "owner": "john",
        }
        ```
        """
        return self.__call("metadata", [metadata_id])

    def metadatas(self, metadata_set_id: int) -> List[Dict]:
        """
        Get all metadatas given a metadata set id.

        Metadatas MAY be ordered with the rank attribute.

        Example output:

        ```
        [
            {
                "id": 1,
                "title": "PNG:ProfileName",
                "set_id": 1,
                "set_title": "exif metas",
                "rank": 0,
                "owner": "john",
            },
            {
                "id": 2,
                "title": "ICC_Profile:GrayTRC",
                "set_id": 1,
                "set_title": "exif metas",
                "rank": 1,
                "owner": "john",
            }
        ]
        ```
        """
        return self.__call("metadatas", [metadata_set_id])

    def metadatasets(self) -> List[Dict]:
        """
        Get the list of all the user's metadata sets.
        For each metadatas set, the number of metadatas is given in metas_count

        Example output:

        ```
        [
            {"id": 1, "title": "exif metas", "owner": "john", "metas_count": 23},
            {"id": 2, "title": "dublin core", "owner": "john", "metas_count": 17}
        ]
        ```
        """
        return self.__call("metadatasets", [])

    def metadatatypes(self) -> List[dict]:
        """
        Get a list of available data types

        Example output:

        ```
        [
            {"id": 1, "title": "text"},
            {"id": 2, "title": "numeric"},
        ]
        ```
        """
        return self.__call("metadatatypes", [])

    def move_collection(
        self, child_collection_id: int, parent_collection_id: int = None
    ) -> bool:
        """
        Move a collection from a parent to another.

        Will return false in the following cases:

        - 'child_collection_id' and 'parent_collection_id' are equal
        - parent collection does not exist
        - parent collection is a descendant of child collection

        If 'parent_collection_id' is null, collection is moved to the root.
        """
        return self.__call(
            "move_collection", [child_collection_id, parent_collection_id]
        )

    def ping(self) -> str:
        """
        This is a test method to ensure the server-client communication works.
        Will return "pong [name authenticated of user]"

        Example output:

        ```
        pong john
        ```
        """
        return self.__call("ping", [])

    def publish_collection(self, collection_id: int) -> bool:
        """
        Mark a collection as public
        """
        return self.__call("publish_collection", [collection_id])

    def remove_meta_from_collection(
        self, collection_id: int, meta_value_id: int
    ) -> bool:
        """
        Remove a meta from a collection given their ids.
        """
        return self.__call(
            "remove_meta_from_collection", [collection_id, meta_value_id]
        )

    def remove_meta_from_resource(self, resource_id: int, meta_value_id: int) -> bool:
        """
        Remove a meta from a resource given their ids.
        """
        return self.__call("remove_meta_from_resource", [resource_id, meta_value_id])

    def remove_resource_from_collection(
        self, resource_id: int, collection_id: int
    ) -> bool:
        """
        Remove a resource from a collection given ids.
        """
        return self.__call(
            "remove_resource_from_collection", [resource_id, collection_id]
        )

    def remove_tag(self, uid: str) -> bool:
        """
        Remove (delete) a tag based on its uid.

        Beware: This will remove ALL associations with the tag.
        """
        return self.__call("remove_tag", [uid])

    def remove_tag_from_collection(self, tag_uid: str, collection_id: int) -> bool:
        """
        Remove tag from a collection based on tag uid and collection id.
        """
        return self.__call("remove_tag_from_collection", [tag_uid, collection_id])

    def remove_tag_from_resource(self, tag_uid: str, resource_id: int) -> bool:
        """
        Remove tag from a resource based on tag uid and resource id.
        """
        return self.__call("remove_tag_from_resource", [tag_uid, resource_id])

    def rename_collection(self, collection_id: int, title: str) -> bool:
        """
        Rename a collection (ie. change its title).
        """
        return self.__call("rename_collection", [collection_id, title])

    def rename_meta(self, meta_id: int, title: str) -> bool:
        """
        Rename a metadata (ie. change its title).
        """
        return self.__call("rename_meta", [meta_id, title])

    def rename_resource(self, resource_id: int, title: str) -> bool:
        """
        Rename a resource (ie. change its title).
        """
        return self.__call("rename_resource", [resource_id, title])

    def replace_file(self, from_resource_id: int, to_resource_id: int) -> bool:
        """
        Replace a file by another using two existing resources.

        The two resources are expected to be of File type. Then the
        following operations are performed:

        - metas from the "ExifTool" set are removed from the destination resource instance
        - metas from the "ExifTool" set are transfered from the source resource instance to the destination resource instance
        - the destination resource instance gets the file hash from the source resource instance
        - the source resource instance is deleted
        - the destination resource instance is saved

        Such that all title/metas/tags/collections of the destination resource instance are untouched,
        excluding exif metas that are transfered from the source.
        """
        return self.__call("replace_file", [from_resource_id, to_resource_id])

    def resource(self, resource_id: int) -> Optional[Dict]:
        """
        Get a resource given its id.

        Example output (file resource):

        ```
        {
            "id": 1,
            "title": "letter",
            "original_name": "letter.txt",
            "type": "text/plain",
            "hash": "0dd93a59aeaccfb6d35b1ff5a49bde1196aa90dfef02892f9aa2ef4087d8738e",
            "metas": null,
            "urls": [],
            "tags": [],
        }
        ```
        """
        return self.__call("resource", [resource_id])

    def resources(
        self,
        collection_id: int,
        include_metas: bool = False,
        limit_from: int = 0,
        limit_to: int = 2000,
    ) -> List[Dict]:
        """
        Get all resources from a collection.

        If 'include_metas' is true, will return the resources metadatas.
        If 'include_metas' is false, 'metas' will be null.

        Different resources types may have different object keys. The bare
        minimum is 'id', 'title' and 'tags'.

        Example output (file resource):

        ```
        [
            {
                "id": 1,
                "title": "letter",
                "original_name": "letter.txt",
                "type": "text/plain",
                "hash": "0dd93a59aeaccfb6d35b1ff5a49bde1196aa90dfef02892f9aa2ef4087d8738e",
                "metas": null,
                "urls": [],
                "tags": [],
            }
        ]
        ```
        """
        return self.__call(
            "resources", [collection_id, include_metas, limit_from, limit_to]
        )

    def set_is_oai_record(self, collection_id: int, is_oai_record: bool = True) -> bool:
        """
        Set/unset the collection as a OAI-PMH record. The creation date
        will be used in OAI-PMH requests.
        """
        return self.__call("set_is_oai_record", [collection_id, is_oai_record])

    def set_representative_resource(
        self, collection_id: int, resource_id: int = None
    ) -> bool:
        """
        Choose a Resource that is the best representation of a collection.
        Typical use case: set a miniature for a collection.

        The Resource does not have to be contained in the collection.

        Resource id may be set set to None/Null.
        """
        return self.__call("set_representative_resource", [collection_id, resource_id])

    def set_tag(self, uid: str, label: str = None, ark: str = None) -> dict:
        """
        Get or create a Tag by uid (unique identifier). 'label' is an optional human-readable name.

        Example output:

        ```
        {
            "id": 1,
            "uid": "PAINTINGS",
            "label": "peintures",
            "ark": null,
        }
        ```
        """
        return self.__call("set_tag", [uid, label, ark])

    def simple_search(self, query: str) -> Dict[str, List]:
        """
        Performs a simple search on resources and collections, based on their titles.

        Example output:

        ```
        {
            "collections": [
                {
                "id": 1,
                "title": "photos",
                "resources_count": 0,
                "children_count": 0,
                "descendants_count": 0,
                "descendants_resources_count": 0,
                "parent": null,
                "children": null,
                "metas": [],
                "public_access": false,
                "tags": [],
                }
            ],
            "resources": [
                {
                "id": 1,
                "title": "letter",
                "original_name": "letter.txt",
                "type": "text/plain",
                "hash": "0dd93a59aeaccfb6d35b1ff5a49bde1196aa90dfef02892f9aa2ef4087d8738e",
                "metas": null,
                "urls": [],
                "tags": [],
                }
            ]
        }
        ```
        """
        return self.__call("simple_search", [query])

    def supported_file_types(self) -> List[Dict]:
        """
        Get a list of all supported file type, complete with their mimes.

        Example output:

        ```
        [
            {
            "mime": "image/jpeg",
            "extensions": [".jpg", ".jpeg"],
            "iiif_support": true,
            }
        ]
        ```
        """
        return self.__call("supported_file_types", [])

    def tags(self) -> List[dict]:
        """
        Returns all tags available to the current user.

        Example output:

        ```
        [
            {
            "id": 1,
            "uid": "PAINTINGS",
            "label": "peintures",
            "ark": null,
            },
            {
            "id": 2,
            "uid": "PHOTOS",
            "label": "photos",
            "ark": null,
            }
        ]
        ```
        """
        return self.__call("tags", [])

    def unpublish_collection(self, collection_id: int) -> bool:
        """
        Mark a collection as private
        """
        return self.__call("unpublish_collection", [collection_id])

    def upload_infos(self, sha256_hash: str) -> Dict:
        """
        Get information for an upload based on the file hash.

        Example output:

        ```
        {
            "status": "not available",
            "id": null,
            "available_chunks":[]
        }
        ```

        "status" being one of "not available", "available" or "incomplete"
        """
        return self.__call("upload_infos", [sha256_hash])
