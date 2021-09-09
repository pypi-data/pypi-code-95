from playmolecule.utils import (
    tempname,
    format_filesize,
    parse_timestamp_utc,
    utc_timestamp_to_local,
    ensurelist,
    _requestURL,
)
import tarfile
import logging
import time
import json
import os
import re


logger = logging.getLogger(__name__)


class DataCenterError(Exception):
    pass


def _throw_error(message, _logger=False):
    if _logger:
        logger.error(message)
    else:
        raise DataCenterError(message)


def _request_url(*args, **kwargs):
    return _requestURL(*args, **kwargs, _throwError=_throw_error)


class DataCenter:
    """Class which manages all the datasets in the PlayMolecule backend

    Parameters
    ----------
    session : Session object
        A Session object
    """

    def __init__(self, session):
        self._session = session

    def get_datasets(
        self,
        public=None,
        datasetid=None,
        remotepath=None,
        useronly=False,
        startswith=None,
        tags=None,
        taggedonly=False,
        completedonly=False,
        _logger=True,
    ):
        """Get a list of datasets filtered by various arguments

        Parameters
        ----------
        public : bool
            If set to True it will only return public datasets. If set to False it will only return private datasets.
            If set to None this parameter will be ignored.
        datasetid : int
            The ID of a specific dataset for which we want to retrieve information
        remotepath : str
            The remote (virtual) path at which the dataset is located
        useronly : bool
            Returns only datasets of the currently logged in user of the Session
        startswith : str
            Returns any datasets whose remote (virtual) path starts with the specific string
        tags : list
            Returns only datasets which have the specified tags
        taggedonly : bool
            If set to True it will only return datasets which have tags
        completedonly : bool
            If set to True it will only return datasets whose jobs have completed successfully
        _logger : bool
            Set to False to reduce verbosity

        Returns
        -------
        datasetlist : list
            A list of datasets retrieved with the above filters

        Examples
        --------
        >>> datasets = dc.get_datasets(remotepath="KdeepTrainer/models/PDBBind2019")
        >>> datasets = dc.get_datasets(tags=["app:kdeep"])
        """
        self._session._require_log_in()

        if tags is not None:
            tags = ensurelist(tags)

        headers = {
            "token": self._session._token,
            "userOnly": str(useronly),
            "datasetId": str(datasetid) if datasetid is not None else "",
            "filePath": remotepath if remotepath is not None else "",
            "public": str(public) if public is not None else "",
            "startsWith": startswith if startswith is not None else "",
            "tags": ",".join(tags) if tags is not None else "",
            "taggedOnly": str(taggedonly),
            "completedOnly": str(completedonly),
        }

        r = _request_url(
            "get",
            f"{self._session._server_endpoint}/datacenter",
            headers=headers,
            _logger=False,
        )
        if r is None:
            return

        datasets = json.loads(r.text)
        for ds in datasets:
            ds["created_at"] = parse_timestamp_utc(ds["created_at"])
            ds["updated_at"] = parse_timestamp_utc(ds["updated_at"])

        if _logger:
            columns = "{:<10} {:<49} {:<20} {:<6} {:<8} {:<36} {:<20} {:<20}"
            print(
                columns.format(
                    "ID",
                    "RemotePath",
                    "Comments",
                    "Public",
                    "FileSize",
                    "ExecID",
                    "DateCreated",
                    "DateUpdated",
                )
            )

            for ds in datasets:
                print(
                    columns.format(
                        ds["id"],
                        ds["filepath"],
                        ds["comments"][:20],
                        "True" if ds["public"] else "False",
                        format_filesize(ds["filesize"]),
                        ds["execid"],
                        utc_timestamp_to_local(ds["created_at"]).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        utc_timestamp_to_local(ds["updated_at"]).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    )
                )
        else:
            return [] if datasets is None else datasets

    def upload_dataset(
        self,
        localpath,
        remotepath,
        comments="",
        public=False,
        execid="",
        overwrite=False,
        tags=None,
        tmpdir=None,
        attempts=1,
        _logger=True,
    ):
        """Uploads a dataset to the backend data center

        Parameters
        ----------
        localpath : str
            The location of the file we want to upload
        remotepath : str
            The remote (virtual) location to which the file should be uploaded
        comments : str
            Comments to attach to the specific dataset
        public : bool
            Set to True to make the dataset public (available to all users)
        execid : str
            Optionally you can relate this dataset to a specific job execution by passing it's job ID
        overwrite : bool
            Set to True to overwrite existing datasets at the specified remote (virtual) location
        tags : list of str
            A list of tags to attach to the specific dataset
        tmpdir : str
            Location to use for creating the upload archive file. The file will be deleted after uploading.
            If set to None it will use /tmp/
        attempts : int
            Number of times to attempt uploading the file. Can help with unstable connections
        _logger : bool
            Set to False to reduce the verbosity
        """
        self._session._require_log_in()

        if not os.path.isfile(localpath) and not os.path.isdir(localpath):
            raise RuntimeError("upload_dataset only accepts files or folders")

        if tags is not None:
            tags = ensurelist(tags)

        fname = os.path.basename(os.path.abspath(localpath))

        tmpfile = tempname(suffix=".tar.gz", tmpdir=tmpdir)
        with tarfile.open(tmpfile, "w:gz") as tar:
            if os.path.isdir(localpath):
                tar.add(localpath, arcname="")
            else:
                tar.add(localpath, arcname=fname)

        # If you specify a remote folder, append the file name for the remote path
        if remotepath.endswith("/"):
            remotepath = remotepath + fname

        # Tags need to be all lower case and strip whitespace
        if tags is not None:
            tags = [tag.lower().strip().replace(" ", "_") for tag in tags]
            for tag in tags:
                if not re.match("^[a-zA-Z0-9_:]+$", tag):
                    raise RuntimeError(
                        "Tags need to be alphanumeric only and can contain _ or :"
                    )

        files = {"uploadfile": (fname, open(tmpfile, "rb"))}
        headers = {"token": self._session._token}
        data = {
            "remotepath": remotepath,
            "comments": comments,
            "public": public,
            "execid": execid,
            "overwrite": overwrite,
            "tags": ",".join(tags) if tags is not None else "",
        }

        uploaded = False
        while not uploaded and attempts > 0:
            try:
                result = _request_url(
                    "post",
                    f"{self._session._server_endpoint}/datacenter",
                    headers=headers,
                    files=files,
                    data=data,
                    _logger=_logger,
                )
            except Exception as e:
                attempts -= 1
                _throw_error(
                    f"Error uploading dataset {localpath} with error {e}. Retrying in 5s. Attempts remaining {attempts}.",
                    _logger,
                )
                time.sleep(5)
            else:
                uploaded = True

        os.remove(tmpfile)

        if not uploaded or result is None:
            _throw_error(
                f"Failed to upload dataset {localpath} to {remotepath}",
                _logger,
            )
            return

        if _logger:
            logger.info(f"File {localpath} was uploaded successfully.")

        return int(result.json()["id"])

    def remove_dataset(self, datasetid, _logger=True):
        """Removes (deletes) a dataset from the backend

        Parameters
        ----------
        datasetid : int
            The ID of the dataset we want to delete
        _logger : bool
            Set to False to reduce verbosity
        """
        self._session._require_log_in()

        headers = {"token": self._session._token}

        r = _request_url(
            "delete",
            f"{self._session._server_endpoint}/datacenter/{datasetid}",
            headers=headers,
            _logger=_logger,
        )

        if r is None:
            return

        if _logger:
            logger.info(f"Dataset {datasetid} was deleted successfully.")

    def download_dataset(self, datasetid, path, tmpdir=None, attempts=1, _logger=True):
        """Download a dataset from the backend

        Parameters
        ----------
        datasetid : int
            The ID of the dataset we want to download
        path : str
            The location to which to download the dataset
        tmpdir : str
            A location to store temporary data. If set to None, the default is /tmp/
        attempts : int
            Number of times to attempt uploading the file. Can help with unstable connections
        _logger : bool
            Set to False to reduce the verbosity

        Examples
        --------
        >>> dc.download_dataset(182, "./dataset_182/")
        """
        self._session._require_log_in()

        if not isinstance(datasetid, int):
            raise RuntimeError("datasetid must be an integer")

        downloaded = False
        while not downloaded and attempts > 0:
            try:
                result = _request_url(
                    "get",
                    f"{self._session._server_endpoint}/datacenter/{datasetid}",
                    headers={"token": self._session._token},
                    _logger=_logger,
                )
            except Exception as e:
                attempts -= 1
                _throw_error(
                    f"Error downloading dataset {datasetid} with error {e}. Retrying in 5s. Attempts remaining {attempts}.",
                    _logger,
                )
                time.sleep(5)
            else:
                downloaded = True

        if not downloaded or result is None:
            _throw_error(
                f"Failed to download dataset {datasetid} to {path}",
                _logger,
            )
            return

        tmpfile = tempname(suffix=".tar.gz", tmpdir=tmpdir)

        with open(tmpfile, "wb") as f:
            f.write(result.content)

        os.makedirs(path, exist_ok=True)

        try:
            with tarfile.open(tmpfile) as tar:
                member = tar.getmembers()[0]
                outname = os.path.abspath(os.path.join(path, member.name))
                tar.extractall(path=path)
            os.remove(tmpfile)
        except Exception as e:
            if os.path.exists(tmpfile):
                os.remove(tmpfile)
            _throw_error(
                f"Error untaring results for dataset {datasetid} with error {e}",
                _logger,
            )
            return

        if _logger:
            logger.info(
                f"Dataset {datasetid} was downloaded successfully to {outname}."
            )

        return outname

    def get_dataset_tags(self, datasetid, _logger=True):
        """Returns tags associated with a dataset

        Parameters
        ----------
        datasetid : int
            The ID of the dataset for which to return tags
        _logger : bool
            Set to False to reduce verbosity
        """
        self._session._require_log_in()

        headers = {"token": self._session._token}

        r = _request_url(
            "get",
            f"{self._session._server_endpoint}/datacenter/{datasetid}/tags",
            headers=headers,
            _logger=_logger,
        )

        if r is None:
            return

        response = json.loads(r.text)
        return [] if response is None else response

    def remove_dataset_tag(self, datasetid, tag, _logger=True):
        """Removes a tag attached to a dataset

        Parameters
        ----------
        datasetid : int
            The ID of the dataset
        tag : str
            The tag we want to remove from the dataset
        _logger : bool
            Set to False to reduce verbosity
        """
        self._session._require_log_in()

        headers = {"token": self._session._token}

        r = _request_url(
            "delete",
            f"{self._session._server_endpoint}/datacenter/{datasetid}/tags/{tag.lower()}",
            headers=headers,
            _logger=_logger,
        )

        if r is None:
            return

        if _logger:
            logger.info(f"Tag {tag} was deleted from dataset {datasetid} successfully.")
