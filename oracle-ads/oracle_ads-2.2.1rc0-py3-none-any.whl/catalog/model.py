#!/usr/bin/env python
# -*- coding: utf-8; -*-

# Copyright (c) 2021 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

import copy
import json
import os
import shutil
import uuid
from types import MethodType
from zipfile import ZipFile
from ads.common import oci_client, auth

import pandas as pd
from IPython.core.display import display
import oci
from oci.config import from_file
from oci.data_science.models import CreateModelDetails, ModelSummary, Model
from oci.data_science.models.model_provenance import ModelProvenance
from oci.data_science.models.update_model_details import UpdateModelDetails
from oci.exceptions import ServiceError

from ads.catalog.summary import SummaryList
from ads.common import utils
from ads.common.utils import is_notebook, print_user_message
from ads.common.model_artifact import ModelArtifact, ConflictStrategy
from ads.config import (
    OCI_IDENTITY_SERVICE_ENDPOINT,
    NB_SESSION_COMPARTMENT_OCID,
    PROJECT_OCID,
    OCI_ODSC_SERVICE_ENDPOINT,
)

update_model_details_attributes = UpdateModelDetails().swagger_types.keys()
model_attributes = list(Model().swagger_types.keys())
model_attributes.append("user_name")
model_provenance_attributes = ModelProvenance().swagger_types.keys()


class ModelSummaryList(SummaryList):
    def __init__(
        self,
        model_catalog,
        model_list,
        response=None,
        datetime_format=utils.date_format,
    ):
        super(ModelSummaryList, self).__init__(
            model_list, datetime_format=datetime_format
        )
        self.mc = model_catalog
        self.response = response

    def __add__(self, rhs):
        return ModelSummaryList(
            self.mc, list.__add__(self, rhs), datetime_format=self.datetime_format
        )

    def __getitem__(self, item):
        return self.mc.get_model(super(ModelSummaryList, self).__getitem__(item).id)

    def sort_by(self, columns, reverse=False):

        """
        Performs a multi-key sort on a particular set of columns and returns the sorted ModelSummaryList
        Results are listed in a descending order by default.

        Parameters
        ----------
        columns: List of string
          A list of columns which are provided to sort on
        reverse: Boolean (defaults to false)
          If you'd like to reverse the results (for example, to get ascending instead of descending results)

        Returns
        -------
        ModelSummaryList: A sorted ModelSummaryList


        """

        return ModelSummaryList(
            self.mc,
            self._sort_by(columns, reverse=reverse),
            datetime_format=self.datetime_format,
        )

    def filter(self, selection, instance=None):
        """
        Filter the model list according to a lambda filter function, or list comprehension.

        Parameters
        ----------
        selection: lambda function filtering model instances, or a list-comprehension
            function of list filtering projects
        instance: list, optional
            list to filter, optional, defaults to self

        Returns
        -------
        ModelSummaryList: A filtered ModelSummaryList
        """
        instance = instance if instance is not None else self

        if callable(selection):
            res = list(filter(selection, instance))
            # lambda filtering
            if len(res) == 0:
                print("No models found")
                return
            return ModelSummaryList(self.mc, res, datetime_format=self.datetime_format)
        elif isinstance(selection, list):
            # list comprehension
            if len(selection) == 0:
                print("No models found")
                return
            return ModelSummaryList(
                self.mc, selection, datetime_format=self.datetime_format
            )
        else:
            raise ValueError(
                "Filter selection must be a function or a ProjectSummaryList"
            )


class ModelCatalog:
    def __init__(
        self, compartment_id=None, ds_client_auth=None, identity_client_auth=None
    ):
        self.compartment_id = (
            NB_SESSION_COMPARTMENT_OCID if compartment_id is None else compartment_id
        )
        if self.compartment_id is None:
            raise ValueError("compartment_id needs to be specified.")

        self.ds_client_auth = (
            ds_client_auth
            if ds_client_auth
            else auth.default_signer(
                {"service_endpoint": OCI_ODSC_SERVICE_ENDPOINT}
                if OCI_ODSC_SERVICE_ENDPOINT
                else {}
            )
        )
        self.identity_client_auth = (
            identity_client_auth
            if identity_client_auth
            else auth.default_signer(
                {"service_endpoint": OCI_IDENTITY_SERVICE_ENDPOINT}
                if OCI_IDENTITY_SERVICE_ENDPOINT
                else {}
            )
        )

        self.ds_client = oci_client.OCIClientFactory(**self.ds_client_auth).data_science
        self.identity_client = oci_client.OCIClientFactory(
            **self.identity_client_auth
        ).identity

        self.short_id_index = {}

    def __getitem__(self, model_id):  # pragma: no cover
        return self.get_model(model_id)

    def __contains__(self, model_id):  # pragma: no cover
        try:
            return self.get_model(model_id) is not None
        except KeyError:
            return False
        except Exception:
            raise

    def __iter__(self):  # pragma: no cover
        return self.list_models().__iter__()

    def __len__(self):  # pragma: no cover
        return len(self.list_models())

    def get_model(self, model_id):
        """
        Get the model based on model_id.

        Parameters
        ----------
        model_id: str, required
            The OCID of the model to get

        Returns
        -------
        model: The oci.data_science.models.Model with the matching ID.
        """
        if not model_id.startswith("ocid"):
            model_id = self.short_id_index[model_id]

        try:
            model_response = self.ds_client.get_model(model_id)
        except ServiceError as e:
            if e.status == 404:
                raise KeyError(e.message) from e
            raise e
        try:
            provenance_response, model_response = self._get_provenance_metadata(
                model_id, model_response
            )
            return self._decorate_model(
                model_response.data,
                self._get_etag(model_response),
                provenance_response.data,
                self._get_etag(provenance_response),
            )
        except:
            raise ValueError(
                f"Unable to fetch model provenance metadata for model {model_id}"
            )

    def _get_provenance_metadata(self, model_id, model_response):
        try:
            provenance_response = self.ds_client.get_model_provenance(model_id)
        except ServiceError as e:
            if e.status == 404:
                try:
                    provenance_response = self.ds_client.create_model_provenance(
                        model_id, ModelProvenance()
                    )
                except ServiceError as e2:
                    raise e2
            else:
                raise e
        return provenance_response, model_response

    def _get_etag(self, response):
        return (
            response.headers["ETag"].split("--")[0]
            if "ETag" in response.headers
            else None
        )

    def _decorate_model(self, model, model_etag, provenance_metadata, provenance_etag):
        model.user_name = ""
        model.swagger_types["user_name"] = "str"
        model._etag = model_etag
        model._provenance_metadata_etag = provenance_etag
        model.ocid = model.id
        try:
            user = self.identity_client.get_user(model.created_by)
            model.user_name = user.data.name
        except:
            pass

        def to_dataframe(model_self):
            attributes = {key: getattr(model_self, key) for key in model_attributes}
            attributes.update(
                {
                    key: getattr(model_self.provenance_metadata, key)
                    for key in model_provenance_attributes
                }
            )
            df = pd.DataFrame.from_dict(
                attributes, orient="index", columns=[""]
            ).dropna()
            return df

        def show_in_notebook(model_self):
            """
            Describe the model by showing it's properties.
            """
            display(model_self)

        def _repr_html_(model_self):
            return (
                model_self.to_dataframe()
                .style.set_properties(**{"margin-left": "0px"})
                .render()
            )

        def activate(model_self):
            """
            Activate the model.
            """
            model_self.lifecycle_state = Model.LIFECYCLE_STATE_ACTIVE

        def deactivate(model_self):
            """
            Deactivate the model.
            """
            model_self.lifecycle_state = Model.LIFECYCLE_STATE_INACTIVE

        def commit(model_self, force=False):
            """
            Commit changes in model.

            Parameters
            ----------
            force: bool
                If True,  any remote changes on this model would be lost
            """
            update_model_details = UpdateModelDetails(
                **{
                    key: getattr(model_self, key)
                    for key in update_model_details_attributes
                }
            )

            # update model
            kwargs = {}
            if not force:
                kwargs["if_match"] = model_self._etag
            self.ds_client.update_model(
                model_self.id, update_model_details=update_model_details, **kwargs
            )
            # store the lifecycle status, as updating the model will delete info not included in "update_model_details"
            lifecycle_status = model_self.lifecycle_state
            model_self.__dict__.update(self.get_model(model_self.id).__dict__)
            model_self.lifecycle_state = lifecycle_status

            # update model state
            if not force:
                kwargs["if_match"] = model_self._etag
            if model_self.lifecycle_state == Model.LIFECYCLE_STATE_ACTIVE:
                self.ds_client.activate_model(model_self.id, **kwargs)
            elif model_self.lifecycle_state == Model.LIFECYCLE_STATE_INACTIVE:
                self.ds_client.deactivate_model(model_self.id, **kwargs)
            model_self.__dict__.update(self.get_model(model_self.id).__dict__)

            # update model provenance
            if model_self.provenance_metadata != ModelProvenance():
                if not force:
                    kwargs["if_match"] = model_self._provenance_metadata_etag
                response = self.ds_client.update_model_provenance(
                    model_self.id, model_self.provenance_metadata, **kwargs
                )

            # get model etag again, as updating model provenance changes it
            model_self.__dict__.update(self.get_model(model_self.id).__dict__)

        def rollback(model_self):
            """
            Get back the model to remote state

            Returns
            -------
            The model from remote state
            """
            model_self.__dict__.update(self.get_model(model_self.id).__dict__)

        model.commit = MethodType(commit, model)
        model.show_in_notebook = MethodType(show_in_notebook, model)
        model.rollback = MethodType(rollback, model)
        model.activate = MethodType(activate, model)
        model.deactivate = MethodType(deactivate, model)
        model.to_dataframe = MethodType(to_dataframe, model)
        model._repr_html_ = MethodType(_repr_html_, model)
        model.provenance_metadata = provenance_metadata
        return model

    def list_models(
        self,
        project_id=None,
        include_deleted=False,
        datetime_format=utils.date_format,
        **kwargs,
    ):
        """
        List all models in a given compartment, or in the current project if project_id is specified.

        Parameters
        ----------
        project_id: str
            The project_id of model
        include_deleted: bool, optional, default=False
            Whether to include deleted models in the returned list
        datetime_format: str, optional, default: '%Y-%m-%d %H:%M:%S'
            Change format for date time fields

        Returns
        -------
        ModelSummaryList: A list of models.
        """
        try:
            list_models_response = self.ds_client.list_models(
                self.compartment_id, project_id=project_id, **kwargs
            )
            if list_models_response.data is None or len(list_models_response.data) == 0:
                print("No model found.")
                return
        except ServiceError as se:
            if se.status == 404:
                raise KeyError(se.message) from se
            else:
                raise

        model_list_filtered = [
            self._decorate_model(model, None, None, None)
            for model in list_models_response.data
            if include_deleted
            or model.lifecycle_state != ModelSummary.LIFECYCLE_STATE_DELETED
        ]
        # handle empty list
        if model_list_filtered is None or len(model_list_filtered) == 0:
            print("No model found.")
            return []

        msl = ModelSummaryList(
            self,
            model_list_filtered,
            list_models_response,
            datetime_format=datetime_format,
        )
        self.short_id_index.update(msl.short_id_index)
        return msl

    def update_model(self, model_id, update_model_details=None, **kwargs):
        """
        Updates a model with given model_id, using the provided update data.

        Parameters
        ----------
        model_id: str
            project_id OCID to update
        update_model_details: oci.data_science.models.UpdateModelDetails
            Contains the update model details data to apply
            Mandatory unless kwargs are supplied
        kwargs: dict, optional
            Update model details can be supplied instead as kwargs

        Returns
        -------
        oci.data_science.models.Model: The updated Model record
        """
        if not model_id.startswith("ocid"):
            model_id = self.short_id_index[model_id]
        if update_model_details is None:
            update_model_details = UpdateModelDetails(
                **{
                    k: v
                    for k, v in kwargs.items()
                    if k in update_model_details_attributes
                }
            )
            update_model_details.compartment_id = self.compartment_id
            # filter kwargs removing used keys
            kwargs = {
                k: v
                for k, v in kwargs.items()
                if k not in update_model_details_attributes
            }
        update_model_response = self.ds_client.update_model(
            model_id, update_model_details, **kwargs
        )
        provenance_response, update_model_response = self._get_provenance_metadata(
            model_id, update_model_response
        )
        return self._decorate_model(
            update_model_response.data,
            self._get_etag(update_model_response),
            provenance_response.data,
            self._get_etag(provenance_response),
        )

    def delete_model(self, model, **kwargs):
        """
        Delete the model based on model_id.

        Parameters
        ----------
        model: str ID or oci.data_science.models.Model,required
            The OCID of the model to delete as a string, or a Model instance

        Returns
        -------
        Bool: `True` if the model was deleted and `False` otherwise
        """
        try:
            model_id = (
                model.id
                if isinstance(model, Model)
                else self.short_id_index[model]
                if not model.startswith("ocid")
                else model
            )
            self.ds_client.delete_model(model_id, **kwargs)
            return True
        except:
            return False

    def download_model(
        self,
        model_id,
        target_dir,
        force_overwrite=False,
        install_libs=False,
        conflict_strategy=ConflictStrategy.IGNORE,
    ):
        """
        Download the model from model_dir to target_dir based on model_id.

        Parameters
        ----------
        model_id: str
            The OCID of the model to download
        target_dir: str
            The target location of model after download
        force_overwrite: bool
            Overwrite target_dir if exists
        install_libs: bool, default: False
            Install the libraries specified in ds-requirements.txt which are missing in the current environment
        conflict_strategy: ConflictStrategy, default: IGNORE
           Determines how to handle version conflicts between the current environment and requirements of
           model artifact
           Valid values: "IGNORE" or ConflictStrategy.IGNORE, "UPDATE" or ConflictStrategy.UPDATE
           IGNORE: Use the installed version in  case of conflict
           UPDATE: Force update dependency to the version required by model artifact in case of conflict

        Returns
        -------
        ModelArtifact: A ModelArtifact instance
        """
        if os.path.exists(target_dir) and os.listdir(target_dir):
            if not force_overwrite:
                raise ValueError(
                    "Target directory already exists. Set 'force_overwrite' to overwrite."
                )
            shutil.rmtree(target_dir)

        try:
            zip_contents = self.ds_client.get_model_artifact_content(
                model_id
            ).data.content
        except ServiceError as se:
            if se.status == 404:
                raise KeyError(se.message) from se
            else:
                raise
        zip_file_path = os.path.join(
            "/tmp", "saved_model_" + str(uuid.uuid4()) + ".zip"
        )
        # write contents to zip file
        with open(zip_file_path, "wb") as zip_file:
            zip_file.write(zip_contents)
        # Extract all the contents of zip file in target directory
        with ZipFile(zip_file_path) as zip_file:
            zip_file.extractall(target_dir)
        os.remove(zip_file_path)
        result = ModelArtifact(
            target_dir, conflict_strategy=conflict_strategy, install_libs=install_libs
        )
        if not install_libs:
            utils.print_user_message(
                "Call <code>install_requirements()</code> on the returned <code>ModelArtifact</code> instance to install the "
                "required dependencies for this model artifact.\n"
                "Any function defined in <code>score.py</code> can be directly invoked on the returned <code>ModelArtifact</code>"
                " instance"
            )
        return result

    def upload_model(
        self,
        model_artifact,
        provenance_metadata=None,
        project_id=None,
        display_name=None,
        description=None,
    ):
        """
        Uploads the model artifact to cloud storage.

        Parameters
        ----------
        model_artifact: `ModelArtifact` instance
            This is built by calling prepare on an `ADSModel` instance
        provenance_metadata: `ModelProvenance`
            Model provenance gives data scientists information about the origin of their model. This information allows data scientists to reproduce
            the development environment in which the model was trained.
        project_id: str, optional
            The project_id of model
        display_name: str, optional
            The name of model
        description: str, optional
            The description of model

        Returns
        -------
        oci.data_science.models.Model: A `Model` instance
        """

        with utils.get_progress_bar(4) as progress:
            project_id = PROJECT_OCID if project_id is None else project_id
            if project_id is None:
                raise ValueError("project_id needs to be specified.")
            schema_file = os.path.join(model_artifact.artifact_dir, "schema.json")
            freeform_tags = {}
            if os.path.exists(schema_file):
                with open(schema_file, "r") as schema:
                    metadata = json.load(schema)
                    freeform_tags = {"problem_type": metadata["problem_type"]}
            progress.update("Creating model in catalog")
            create_model_details = CreateModelDetails(
                display_name=display_name,
                description=description,
                project_id=project_id,
                compartment_id=self.compartment_id,
            )
            # freeform_tags=freeform+tags)
            model = self.ds_client.create_model(create_model_details)
            self._upload_model_artifact(model.data.id, model_artifact, progress)
            if provenance_metadata is not None:
                progress.update("Save provenance metadata")
                self.ds_client.create_model_provenance(
                    model.data.id, provenance_metadata
                )
            else:
                progress.update()
            progress.update("Done")
            return self.get_model(model.data.id)

    def _upload_model_artifact(self, model_id, model_artifact, progress):
        # zip model_dir
        progress.update("Generating model artifact zip")
        files_to_upload = model_artifact._get_files()
        artifact = "/tmp/saved_model_" + str(uuid.uuid4()) + ".zip"
        print("artifact:" + artifact)
        zf = ZipFile(artifact, "w")
        for matched_file in files_to_upload:
            zf.write(
                os.path.join(model_artifact.artifact_dir, matched_file),
                arcname=matched_file,
            )
        zf.close()
        progress.update("Uploading model artifact")
        with open(artifact, "rb") as file_data:
            bytes_content = file_data.read()
            self.ds_client.create_model_artifact(
                model_id,
                bytes_content,
                content_disposition=f'attachment; filename="{model_id}.zip"',
            )
        os.remove(artifact)

        if is_notebook():
            print_user_message(
                "If you wish to clear space in local storage after save or upload model, run <code>rm -rf {}</code>.".format(
                    model_artifact.artifact_dir
                ),
                display_type="info",
                title=None,
            )
        else:
            print(
                "If you wish to clear space in local storage folder after save or upload model, run 'rm -rf {}'.".format(
                    model_artifact.artifact_dir
                )
            )
