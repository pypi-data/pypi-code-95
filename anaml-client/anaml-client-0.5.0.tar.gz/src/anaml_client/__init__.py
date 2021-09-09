#
#  Copyright 2021 Simple Machines Pty Ltd - All Rights Reserved.
#
#  This file is part of Anaml.
#
#  Unauthorized copying and/or distribution of this file, via any medium
#  is strictly prohibited.
#

"""Interact with an Anaml server using the REST API."""

from __future__ import annotations

import base64
import glob
import json
import logging
import os.path
import typing
from typing import List, Optional, Union
from uuid import UUID

import requests

# Import the optional libraries during type-checking. This allows us to use them
# in type annotations without insisting that every user install PySpark whether
# or not they will use it.
#
# NB: This relies on the __future__ import changing the way that type annotations
# are processed.
#
# This is supported in Python 3.7+
if typing.TYPE_CHECKING:
    import pandas
    import pyspark.sql
    import s3fs
    from google.cloud import bigquery

from .models.branch import BranchName
from .models.checks import Check, CheckCreationRequest, CheckId
from .models.cluster import Cluster, ClusterId, ClusterName
from .models.commit import Commit, CommitId
from .models.destination import (
    Destination, BigQueryDestination, GCSDestination, HDFSDestination, LocalDestination, S3ADestination,
    S3Destination, DestinationId, DestinationName
)
from .models.destination_reference import TableDestinationReference, FolderDestinationReference
from .models.generated_features import GeneratedFeatures
from .models.feature import Feature
from .models.feature_creation_request import FeatureCreationRequest
from .models.feature_id import FeatureId, FeatureName
from .models.feature_run_summaries import FeatureRunSummary
from .models.feature_set import FeatureSet, FeatureSetId, FeatureSetName
from .models.feature_store import FeatureStore, FeatureStoreName, FeatureStoreId
from .models.feature_store_run import FeatureStoreRun
from .models.feature_template import FeatureTemplate, TemplateId, TemplateName
from .models.feature_template_creation_request import FeatureTemplateCreationRequest
from .models.file_format import CSV, FileFormat, Parquet, Orc
from .models.jobs import RunStatus, FeatureStoreRunId
from .models.merge_request import MergeRequest, MergeRequestId
from .models.ref import Ref
from .models.table import Table, TableId
from . import version


__version__ = version.__version__

log = logging.getLogger(__name__)

_NO_FEATURES = """No feature instances were generated for the following """
_NO_FEATURES += """features:\n{the_features}.\n"""
_NO_FEATURES += """This could be because the underlying dataset was empty, """
_NO_FEATURES += """or because a predicate or window in the feature excluded"""
_NO_FEATURES += """ all records in the dataset."""


class Anaml:
    """Anaml is a service class providing access to all functionality."""

    _bigquery_client_instance: Optional[bigquery.Client] = None
    _s3fs_client_instance: Optional[s3fs.S3FileSystem] = None

    def __init__(self, url: str, apikey: str, secret: str, ref: Optional[Ref] = None):
        """Create a new `Anaml` instance.

        Access to the API requires a Personal Access Token which can be obtain on the users profile page
        on the web interface.

        Arguments:
            url: Base URL for the Anaml server API. e.g. https://anaml.company.com/api
            apikey: API key for Personal Access Token.
            secret: API secret for Personal Access Token.
            ref: The BranchRef or CommitRef reference to act on.
        """
        self._url = url
        self._token = base64.b64encode(bytes(apikey + ':' + secret, 'utf-8')).decode('utf-8')
        self._headers = {'Authorization': 'Basic ' + self._token}
        if ref is not None:
            self._ref = {ref.adt_type: ref.ref}
        else:
            self._ref = {}

    def __enter__(self):
        """Enter the runtime context client in a context manager."""
        return self

    def __exit__(self, exc_type: typing.Type[Exception], exc_value: Exception, traceback):
        """Exit the runtime context related to this object.

        All internal clients and services are stopped.
        """
        self.close()
        # We don't handle any exceptions: the context manager machinery should not swallow them.
        return None

    @property
    def _bigquery_client(self) -> bigquery.Client:
        """Initialise and cache a BigQuery client object."""
        if self._bigquery_client_instance is None:
            from google.cloud import bigquery
            # TODO: Do we need to support manual configuration of the BigQuery client?
            self._bigquery_client_instance = bigquery.Client()
        return self._bigquery_client_instance

    @property
    def _s3fs_client(self) -> s3fs.S3FileSystem:
        """Initialise and cache an s3fs filesystem object."""
        if self._s3fs_client_instance is None:
            import s3fs
            # TODO: Do we need to support manual configuration of the S3 client?
            self._s3fs_client_instance = s3fs.S3FileSystem(anon=False)
        return self._s3fs_client_instance

    def close(self) -> None:
        """Close and discard internal clients and services."""
        if self._bigquery_client_instance is not None:
            self._bigquery_client_instance.close()
            self._bigquery_client_instance = None
        if self._s3fs_client_instance is not None:
            self._s3fs_client_instance = None

    def with_ref(self, new_ref: Ref) -> Anaml:
        """Return a new instance of "Anaml" that will act on the given `new_ref`.

        Args:
            new_ref: A reference to a branch or commit.

        Returns:
            A new Anaml instance configured to use the new reference.
        """
        # This is a bit hacky
        new_anaml = Anaml(self._url, "", "", new_ref)
        new_anaml._token = self._token
        new_anaml._headers = self._headers

        return new_anaml

    def _get(self, path: str, query: Optional[dict] = None):
        """Send a GET request to the Anaml server."""
        if query is None:
            query = {}
        params = {**query, **self._ref}
        return requests.get(self._url + path, params=params, headers=self._headers)

    def _put(self, part: str, json):
        """Send a PUT request to the Anaml server."""
        return requests.put(self._url + part, params=self._ref, json=json, headers=self._headers)

    def _post(self, part, json, **kwargs):
        """Send a POST request to the Anaml server."""
        return requests.post(self._url + part, params=self._ref, json=json, headers=self._headers, **kwargs)

    # Commits and Branches

    def get_current_commit(self, branch: Union[BranchName, str]) -> Commit:
        """Get the current commit for a branch.

        Args:
            branch: Name of the branch to inspect.

        Returns:
            The commit currently at the tip of the named branch.
        """
        r = self._get(f"/branch/{str(branch)}")
        result = self._json_or_handle_errors(r)
        return Commit.from_json(result)

    # Cluster-related functions

    def get_clusters(self) -> List[Cluster]:
        """Get a list of clusters from the Anaml server.

        Returns:
              A list of clusters.
        """
        r = self._get("/cluster")
        result = self._json_or_handle_errors(r)
        return [Cluster.from_json(d) for d in result]

    def get_cluster_by_id(self, cluster_id: Union[ClusterId, int]) -> Cluster:
        """Get a cluster definition from the Anaml server.

        Args:
            cluster_id: Unique identifier of the cluster definition to retrieve.

        Returns:
            The requested cluster definition, if it exists.
        """
        r = self._get(f"/cluster/{int(cluster_id)}")
        result = self._json_or_handle_errors(r)
        return Cluster.from_json(result)

    def get_cluster_by_name(self, name: Union[ClusterName, str]) -> Cluster:
        """Get a cluster definition from the Anaml server.

        Args:
            name: Name of cluster definition to retrieve.

        Returns:
            The requested cluster definition, if it exists.
        """
        r = self._get("/cluster", query={'name': str(name)})
        result = self._json_or_handle_errors(r)
        return Cluster.from_json(result)

    # Feature-related functions
    def get_features(self) -> List[Feature]:
        """Get a list of all features from the Anaml server.

        Returns:
            A list of features.
        """
        r = self._get("/feature")
        result = self._json_or_handle_errors(r)
        return [Feature.from_json(d) for d in result]

    def get_feature_by_id(self, feature_id: Union[FeatureId, int]) -> Feature:
        """Get a feature from the Anaml server.

        Args:
            feature_id: Unique identifier of the feature to retrieve.

        Returns:
            The requested feature, if it exists.
        """
        r = self._get(f"/feature/{int(feature_id)}")
        result = self._json_or_handle_errors(r)
        return Feature.from_json(result)

    def get_feature_by_name(self, name: Union[FeatureName, str]) -> Feature:
        """Get a feature from the Anaml server.

        Args:
            name: Name of the feature to retrieve.

        Returns:
            The requested feature, if it exists.
        """
        r = self._get("/feature", query={'name': str(name)})
        result = self._json_or_handle_errors(r)
        return Feature.from_json(result)

    def get_generated_features(
        self,
        feature_store: Union[FeatureStoreName, str],
        primary_key: int
    ) -> GeneratedFeatures:
        """Get the features generated from a feature store for a particular primary key value.

        Args:
            feature_store: Name of the feature store.
            primary_key: Primary key of the entity to get.

        Returns:
            The features for the given primary key in the named feature store.
        """
        r = self._get("/generated-feature/" + feature_store + "/" + str(primary_key))
        result = self._json_or_handle_errors(r)
        return GeneratedFeatures.from_json(result)

    def create_feature(self, feature: FeatureCreationRequest) -> Feature:
        """Create a feature definition on the Anaml server.

        Args:
            feature: The feature definition.

        Returns:
            The new feature.
        """
        r = self._post("/feature", json=feature.to_json())
        id = self._int_or_handle_errors(r)
        return self.get_feature_by_id(id)

    def update_feature(self, feature: Feature) -> Feature:
        """Update an existing feature definition on the Anaml server.

        Args:
            feature: The feature definition.

        Returns:
            The feature definition, with its unique identifier and other computed
            fields updated.
        """
        r = self._put(f"/feature/{str(feature.id.value)}", json=feature.to_json())
        # TODO: Is this, in fact, an int?
        _ = self._int_or_handle_errors(r)
        return self.get_feature_by_id(int(feature.id.value))

    def preview_feature(self, feature: Feature) -> None:
        """Show a matplotlib plot for the preview statistics of a feature.

        Args:
            feature: a Feature object
        """
        r = self._post("/feature-preview", json={"features": [feature.to_json()]})
        result = self._json_or_handle_errors(r)

        feature_stats = [
            fs
            for pd in self._to_list(result.get("previewData"))
            for fss in self._to_list(pd.get("featureStatistics"))
            for fs in fss
        ]
        for fs in feature_stats:
            self._build_feature_plots(fs)
        self._warn_empty_feature_stats([
            fs["featureName"]
            for fs in feature_stats if fs.get("adt_type") == "empty"
        ])

    def sample_feature(self, feature: Feature) -> pandas.DataFrame:
        """Generate a sample of feature values.

        Arguments:
            feature: a Feature object

        Returns:
            a pandas dataframe of the feature sample values
        """
        import pandas

        r = self._post("/feature-sample", json={"features": [feature.to_json()]})
        result = self._json_or_handle_errors(r)

        return pandas.DataFrame(result)

    def create_feature_template(self, template: FeatureTemplateCreationRequest) -> FeatureTemplate:
        """Create a new feature template.

        Args:
            template: Details of the feature template.

        Returns:
            The new feature template.
        """
        r = self._post("/feature-template", json=template.to_json())
        id = self._int_or_handle_errors(r)
        return self.get_feature_template_by_id(id)

    def get_feature_templates(self) -> List[FeatureTemplate]:
        """Get a list of all features templates from the Anaml server.

        Returns:
            A list of all feature templates.
        """
        r = self._get("/feature-template")
        result = self._json_or_handle_errors(r)
        return [FeatureTemplate.from_json(d) for d in result]

    def get_feature_template_by_id(self, feature_template_id: Union[TemplateId, int]) -> FeatureTemplate:
        """Get a feature template from the Anaml server.

        Args:
            feature_template_id: Unique identifier of the feature template to retrieve.

        Returns:
            The requested feature template, if it exists.
        """
        r = self._get(f"/feature-template/{int(feature_template_id)}")
        result = self._json_or_handle_errors(r)
        return FeatureTemplate.from_json(result)

    def get_feature_template_by_name(self, name: Union[TemplateName, str]) -> FeatureTemplate:
        """Get a feature template from the Anaml server.

        Args:
            name: Name of the feature template to retrieve.

        Returns:
            The requested feature template, if it exists.
        """
        r = self._get("/feature-template", query={'name': str(name)})
        result = self._json_or_handle_errors(r)
        return FeatureTemplate.from_json(result)

    # Table-related functions
    def get_tables(self) -> List[Table]:
        """Get a list of all tables from the Anaml server.

        Returns:
            A list of tables.
        """
        r = self._get("/table")
        result = self._json_or_handle_errors(r)
        return [Table.from_json(d) for d in result]

    def get_table_by_id(self, table_id: Union[TableId, int]) -> Table:
        """Get a table from the Anaml server.

        Args:
            table_id: Unique identifier of the table to retrieve.

        Returns:
            The requested table, if it exists.
        """
        r = self._get(f"/table/{int(table_id)}")
        result = self._json_or_handle_errors(r)
        return Table.from_json(result)

    def get_table_by_name(self, name: str) -> Table:
        """Get a table from the Anaml server.

        Args:
            name: Name of the table to retrieve.

        Returns:
            The requested table, if it exists.
        """
        r = self._get("/table", query={'name': str(name)})
        result = self._json_or_handle_errors(r)
        return Table.from_json(result)

    # Destination-related functions
    def get_destinations(self) -> List[Destination]:
        """Get a list of all destinations from the Anaml server.

        Returns:
            A list of destinations.
        """
        r = self._get("/destination")
        result = self._json_or_handle_errors(r)
        return [Destination.from_json(d) for d in result]

    def get_destination_by_id(self, destination_id: Union[DestinationId, int]) -> Destination:
        """Get a destination from the Anaml server.

        Args:
            destination_id: Unique identifier of the destination.

        Returns:
            The destination, if it exists.
        """
        r = self._get(f"/destination/{int(destination_id)}")
        result = self._json_or_handle_errors(r)
        return Destination.from_json(result)

    def get_destination_by_name(self, name: Union[DestinationName, str]) -> Destination:
        """Get a destination from the Anaml server.

        Args:
            name: Name of the destination.

        Returns:
            The destination, if it exists.
        """
        r = self._get("/destination", query={'name': str(name)})
        result = self._json_or_handle_errors(r)
        return Destination.from_json(result)

    def get_feature_run_summary(self, feature_id: Union[FeatureId, int]) -> FeatureRunSummary:
        """Get a summary of the most recent run of a feature.

        Args:
            feature_id: Unique identifier of the feature.

        Returns:
            A summary of the given feature from the most recent feature store run.
        """
        r = self._get(f"/feature/{int(feature_id)}/latest-run-statistics")
        result = self._json_or_handle_errors(r)
        return FeatureRunSummary.from_json(result)

    def get_feature_sets(self) -> List[FeatureSet]:
        """Get a list of feature sets from the Anaml server.

        Returns:
            A list of feature sets.
        """
        r = self._get("/feature-set")
        result = self._json_or_handle_errors(r)
        return [FeatureSet.from_json(r) for r in result]

    def get_feature_set_by_id(self, feature_set_id: Union[FeatureSetId, int]) -> FeatureSet:
        """Get a feature set from the Anaml server.

        Args:
            feature_set_id: Unique identifier of the feature set.

        Returns:
            The feature set, if it exists.
        """
        r = self._get(f"/feature-set/{int(feature_set_id)}")
        result = self._json_or_handle_errors(r)
        return FeatureSet.from_json(result)

    def get_feature_set_by_name(self, name: Union[FeatureSetName, str]) -> FeatureSet:
        """Get a feature set from the Anaml server.

        Args:
            name: Name of the feature set.

        Returns:
            The feature set, if it exists.
        """
        r = self._get("/feature-set", query={'name': str(name)})
        result = self._json_or_handle_errors(r)
        return FeatureSet.from_json(result)

    def get_run_for_feature_set(self, feature_set_id: Union[FeatureSetId, int]) -> FeatureStoreRun:
        """Get the most recent feature store run for the given feature set.

        Args:
            feature_set_id: The unique identifier of the feature set.

        Returns:
            The most recent feature store run for that feature set.
        """
        r = self._get(f"/feature-set/{int(feature_set_id)}/latest-run-statistics")
        result = self._json_or_handle_errors(r)
        return FeatureStoreRun.from_json(result)

    def get_feature_stores(self) -> List[FeatureStore]:
        """Get a list of all feature stores from the Anaml server.

        Returns:
            A list of feature stores.
        """
        r = self._get("/feature-store")
        result = self._json_or_handle_errors(r)
        return [FeatureStore.from_json(r) for r in result]

    def get_feature_store_by_id(self, feature_store_id: Union[FeatureStoreId, int]) -> FeatureStore:
        """Get a feature store from the Anaml server.

        Args:
            feature_store_id: Unique identifier of the feature store.

        Returns:
            The feature store, if it exists.
        """
        r = self._get(f"/feature-store/{int(feature_store_id)}")
        result = self._json_or_handle_errors(r)
        return FeatureStore.from_json(result)

    def get_feature_store_by_name(self, name: Union[FeatureStoreName, str]) -> FeatureStore:
        """Get a feature store from the Anaml server.

        Args:
            name: Name of the feature store.

        Returns:
            The feature store, if it exists.
        """
        r = self._get("/feature-store", query={'name': str(name)})
        result = self._json_or_handle_errors(r)
        return FeatureStore.from_json(result)

    def get_feature_store_runs(
        self,
        feature_store_id: Union[FeatureStoreId, int],
        num: Optional[int] = None
    ) -> List[FeatureStoreRun]:
        """Get a list of all runs of a given feature store from the Anaml server.

        Args:
            feature_store_id: The unique identifier of a feature store.
            num: Optional. Maximum number of results to return.

        Returns:
            A list of runs of the given feature store.
        """
        q = {}
        if num is not None:
            q['num'] = num
        r = self._get(f"/feature-store/{int(feature_store_id)}/run", query=q)
        result = self._json_or_handle_errors(r)
        return [FeatureStoreRun.from_json(r) for r in result]

    def get_feature_store_run(
        self,
        feature_store_id: Union[FeatureStoreId, int],
        run_id: Union[FeatureStoreRunId, int]
    ) -> FeatureStoreRun:
        """Get the details for a feature store run from the Anaml server.

        Args:
            feature_store_id: The unique identifier of a feature store.
            run_id: The unique identifier of a run of that feature store.

        Returns:
             Details of the given feature store run.
        """
        r = self._get(f"/feature-store/{int(feature_store_id)}/run/{int(run_id)}")
        result = self._json_or_handle_errors(r)
        return FeatureStoreRun.from_json(result)

    def get_latest_feature_store_run_by_name(self, feature_store_name: Union[FeatureStoreName, str]) -> FeatureStoreRun:
        """Get the most recent run of the named feature store from the Anaml server.

        Args:
            feature_store_name: The name of the feature store.

        Returns:
            Details of the feature store run.

        Raises:
            IndexError: When the named feature store has no runs.
        """
        feature_store = self.get_feature_store_by_name(feature_store_name)
        # TODO: Extend server to provide an end
        runs = self.get_feature_store_runs(feature_store_id=feature_store.id.value, num=1)
        return runs[0]

    def get_merge_requests(self, limit: int = 10) -> List[MergeRequest]:
        """List merge requests from the Anaml server.

        Args:
            limit: The maximum number of objects to return.

        Returns:
            A list of merge requests.
        """
        r = self._get("/merge-request")
        result = self._json_or_handle_errors(r)
        return [
            MergeRequest.from_json(r) for r in result
        ]

    def get_merge_request(self, merge_request_id: Union[MergeRequestId, int]) -> MergeRequest:
        """Get a merge request from the Anaml server.

        Args:
            merge_request_id: Unique identifier of the merge request.

        Returns:
            The merge request, if it exists.
        """
        r = self._get(f"/merge-request/{int(merge_request_id)}")
        result = self._json_or_handle_errors(r)
        return MergeRequest.from_json(result)

    # Checks
    def get_checks(self, commit_id: Union[CommitId, UUID]) -> List[Check]:
        """Get checks for a given commit from the Anaml server.

        Args:
            commit_id: Unique identifier of the commit.

        Returns:
            A list of checks associated with the given commit.
        """
        r = self._get(f"/checks/{str(commit_id)}")
        result = self._json_or_handle_errors(r)
        return [
            Check.from_json(r) for r in result
        ]

    def get_check(self, commit_id: Union[CommitId, UUID], check_id: Union[CheckId, int]) -> Check:
        """Get a specific check for given a commit_id from the Anaml server.

        Args:
            commit_id: Unique identifier of the commit.
            check_id: Unique identifier of the check.

        Returns:
            The check, if it exists.
        """
        r = self._get(f"/checks/{str(commit_id)}/{int(check_id)}")
        result = self._json_or_handle_errors(r)
        return Check.from_json(result)

    def create_check(self, commit: Union[CommitId, UUID], check: CheckCreationRequest) -> Check:
        """Create a new Check for a commit.

        Args:
            commit: The commit being checked.
            check: The details of the check.

        Returns:
            The check object, with unique identifier and other computed fields updated.
        """
        r = self._post(f"/checks/{str(commit)}", json=check.to_json())
        id = self._int_or_handle_errors(r)
        return self.get_check(commit, id)

    def update_check(self, check: Check) -> Check:
        """Get Checks from the Anaml server.

        Args:
            check: The check details to be saved.

        Returns:
            The check object, with unique identifier and other computed fields updated.
        """
        r = self._put("/checks/" + str(check.commit.value) + "/" + str(check.id.value), json=check.to_json())
        result = self._json_or_handle_errors(r)
        return Check.from_json(result)

    #####################
    # Load feature data #
    #####################

    def load_features_to_pandas(self, run: FeatureStoreRun) -> pandas.DataFrame:
        """Load the data from a collection of features to a Pandas data frame.

        This method supports some but not all of the data stores available to
        the Anaml server. Where necessary, you may need to configure authentication
        to each data store separately using the appropriate configuration file,
        environment variables, or other mechanism.

        Args:
            run: A successful run of the feature store to be loaded.

        Warning: This method will attempt to load all of the data in the given
        feature store, whether or not your Python process has enough memory to
        store it.

        Returns:
            A Pandas dataframe.
        """
        return self._load_features_to_dataframe(run)

    def load_features_to_spark(
        self,
        run: FeatureStoreRun,
        *,
        spark_session: pyspark.sql.SparkSession
    ) -> pandas.DataFrame:
        """Load the data from a collection of features to a Spark data frame.

        This method supports some but not all of the data stores available to
        the Anaml server.

        Args:
            run: A successful run of the feature store to be loaded.
            spark_session: A running Spark session to load the data.

        The Spark session must have the appropriate libraries and configuration
        to access the underlying data store.

        Returns:
            A Spark dataframe object.
        """
        return self._load_features_to_dataframe(run, spark_session=spark_session)

    def _load_features_to_dataframe(
            self,
            run: FeatureStoreRun,
            *,
            spark_session: Optional[pyspark.sql.SparkSession] = None,
    ) -> Union[pandas.DataFrame, pyspark.sql.DataFrame]:
        """Load the data from a feature store into a data frame.

        Args:
            run: A run from a feature store.
            spark_session: Optional Spark session to load the data.

        Returns:
              When `spark_session` is given, a Spark data frame will be created and returned.
              Otherwise, a Pandas data frame will be created and returned.
        """
        if run.status != RunStatus.Completed:
            log.debug(f"Attempted to load data from feature store run id={run.id.value}, status={run.status.value}")
            raise ValueError("The feature store run is not complete")
        # TODO: We should thing about using Version here.
        store = self.get_feature_store_by_id(run.featureStoreId.value)
        # Loop through the destinations and attempt to load them. They should all contain the same data, so we'll
        # take the first one we find that actually returns a dataframe.
        dataframe = None
        for dest_ref in store.destinations:
            dest = self.get_destination_by_id(dest_ref.destinationId.value)
            if isinstance(dest_ref, TableDestinationReference):
                if isinstance(dest, BigQueryDestination) and spark_session is not None:
                    project, dataset = dest.path.split(":")
                    ref = "{project}.{dataset}.{table}".format(
                        project=project,
                        dataset=dataset,
                        table=dest_ref.tableName
                    )
                    dataframe = spark_session.read.format('bigquery').option('table', ref).load()
                elif isinstance(dest, BigQueryDestination) and spark_session is None:
                    # We're using the BigQuery client library instead of the Pandas support.
                    # More information: https://cloud.google.com/bigquery/docs/pandas-gbq-migration
                    from google.cloud import bigquery
                    project, dataset = dest.path.split(":")
                    ref = bigquery.TableReference(
                        dataset_ref=bigquery.DatasetReference(project=project, dataset_id=dataset),
                        table_id=dest_ref.tableName
                    )
                    dataframe = self._bigquery_client.list_rows(
                        table=ref,
                        # TODO: Should we restrict the columns we want to fetch?
                        selected_fields=None,
                    ).to_dataframe()
                # TODO: Implement support for loading data from Hive.
                # TODO: Implement support for loading data from HDBC.
                else:
                    log.debug(f"Cannot load table data from {type(dest).__name__}; skipping.")
            elif isinstance(dest_ref, FolderDestinationReference):
                if isinstance(dest, GCSDestination) and spark_session is not None:
                    url = "gs://{bucket}/{prefix}/".format(
                        bucket=dest.bucket,
                        prefix=f"{dest.path.strip('/')}/{dest_ref.folder.strip('/')}"
                    )
                    spark_options = {}
                    if isinstance(dest.fileFormat, CSV):
                        spark_options['header'] = dest.fileFormat.includeHeader
                    dataframe = spark_session.read.load(path=url, format=dest.fileFormat.adt_type, **spark_options)
                elif isinstance(dest, GCSDestination) and spark_session is None:
                    url = "gs://{bucket}/{prefix}/**{suffix}".format(
                        bucket=dest.bucket,
                        prefix=f"{dest.path.strip('/')}/{dest_ref.folder.strip('/')}",
                        suffix=self._file_format_suffix(dest.fileFormat)
                    )
                    dataframe = self._load_pandas_from_files(
                        urls=[url],
                        format=dest.fileFormat
                    )
                elif isinstance(dest, HDFSDestination) and spark_session is not None:
                    url = "hdfs://{path}".format(
                        path=f"{dest.path.strip('/')}/{dest_ref.folder.strip('/')}"
                    )
                    spark_options = {}
                    if isinstance(dest.fileFormat, CSV):
                        spark_options['header'] = dest.fileFormat.includeHeader
                    dataframe = spark_session.read.load(path=url, format=dest.fileFormat.adt_type, **spark_options)
                # TODO: Load Pandas data frame from HDFS.
                elif isinstance(dest, LocalDestination) and spark_session is not None:
                    url = f"/{dest.path.strip('/')}/{dest_ref.folder.strip('/')}"
                    spark_options = {}
                    if isinstance(dest.fileFormat, CSV):
                        spark_options['header'] = dest.fileFormat.includeHeader
                    dataframe = spark_session.read.load(path=url, format=dest.fileFormat.adt_type, **spark_options)
                elif isinstance(dest, LocalDestination) and spark_session is None:
                    url = "{prefix}/**/*{suffix}".format(
                        prefix=f"/{dest.path.strip('/')}/{dest_ref.folder.strip('/')}",
                        suffix=self._file_format_suffix(dest.fileFormat)
                    )
                    dataframe = self._load_pandas_from_files(
                        urls=filter(os.path.isfile, glob.iglob(url, recursive=True)),
                        format=dest.fileFormat
                    )
                elif isinstance(dest, S3ADestination) and spark_session is not None:
                    url = "s3a://{bucket}/{prefix}/".format(
                        bucket=dest.bucket,
                        prefix=f"{dest.path.strip('/')}/{dest_ref.folder.strip('/')}",
                    )
                    spark_options = {}
                    if isinstance(dest.fileFormat, CSV):
                        spark_options['header'] = dest.fileFormat.includeHeader
                    dataframe = spark_session.read.load(path=url, format=dest.fileFormat.adt_type, **spark_options)
                elif isinstance(dest, S3Destination) and spark_session is not None:
                    url = "s3://{bucket}/{prefix}/".format(
                        bucket=dest.bucket,
                        prefix=f"{dest.path.strip('/')}/{dest_ref.folder.strip('/')}"
                    )
                    spark_options = {}
                    if isinstance(dest.fileFormat, CSV):
                        spark_options['header'] = dest.fileFormat.includeHeader
                    dataframe = spark_session.read.load(path=url, format=dest.fileFormat.adt_type, **spark_options)
                elif isinstance(dest, S3Destination) or isinstance(dest, S3ADestination):
                    url = "{bucket}/{prefix}/**{suffix}".format(
                        bucket=dest.bucket,
                        prefix=f"{dest.path.strip('/')}/{dest_ref.folder.strip('/')}",
                        suffix=self._file_format_suffix(dest.fileFormat)
                    )
                    dataframe = self._load_pandas_from_files(
                        urls=self._s3fs_client.glob(path=url),
                        format=dest.fileFormat
                    )
                else:
                    log.debug(f"Cannot load folder data from {type(dest).__name__}; skipping.")
            else:
                log.debug(f"Cannot load data from {type(dest_ref).__name__} references; skipping.")
            if dataframe is not None:
                return dataframe

        # If we haven't returned, then there were no supported destinations.
        raise NotImplementedError("No supported data stores available.")

    @staticmethod
    def _load_pandas_from_files(
        urls: typing.Iterable[str],
        format: FileFormat
    ) -> Optional[pandas.DataFrame]:
        """Load a folder of datafiles in Google Cloud Storage into a Pandas data frame.

        Args:
            urls: Collection of paths/URLs to the data files.
            format: Format of the data files.

        Warning: This method makes no attempt to check that the requested data will fit into available memory.
        """
        import pandas
        if isinstance(format, Parquet):
            return pandas.concat(pandas.read_parquet(url) for url in urls)
        elif isinstance(format, Orc):
            return pandas.concat(pandas.read_orc(url) for url in urls)
        elif isinstance(format, CSV):
            return pandas.concat(pandas.read_csv(url) for url in urls)
        else:
            raise ValueError(f"Cannot load unsupported format: {format.adt_type}")

    def _build_feature_plots(self, fs):
        [self._build_numerical_plots(qdata, fs.get("featureName"))
         for qdata in self._to_list(fs.get("quantiles"))]
        [self._build_categorical_plots(qdata, fs.get("featureName"))
         for qdata in self._to_list(fs.get("categoryFrequencies"))]

    @staticmethod
    def _build_numerical_plots(qdata, title: str) -> None:
        import numpy
        import seaborn
        from matplotlib import pyplot
        seaborn.set_style('whitegrid')
        pyplot.subplot(211)
        seaborn.kdeplot(x=numpy.array(qdata))
        pyplot.title(title)
        pyplot.subplot(212)
        seaborn.boxplot(x=numpy.array(qdata))
        pyplot.tight_layout()
        pyplot.show()

    @staticmethod
    def _build_categorical_plots(qdata, title: str) -> None:
        from matplotlib import pyplot
        import seaborn
        seaborn.set_style('whitegrid')
        seaborn.catplot(x="category", y="frequency", kind="bar", data=pandas.DataFrame(qdata))
        pyplot.title(title)
        pyplot.show()

    A = typing.TypeVar('A')

    @staticmethod
    def _to_list(gotten: Optional[A]) -> List[A]:
        return [] if gotten is None else [gotten]

    @staticmethod
    def _warn_empty_stats(features: List[str]):
        if features:
            log.warning(_NO_FEATURES.format(thefeatures=', '.join(features)))

    @staticmethod
    def _json_or_handle_errors(r):
        if r.ok:
            try:
                result = r.json()
                return result
            except json.JSONDecodeError:
                # Sorry, (no or invalid) JSON here
                log.error("No or invalid JSON received from server")
                log.error("Response content: " + r.content)
                r.raise_for_status()
        else:
            if "errors" in r:
                log.error(json.dumps(r._get("errors"), indent=4))

        r.raise_for_status()

    @staticmethod
    def _int_or_handle_errors(r):
        if r.ok:
            return int(r.text)
        else:
            if "errors" in r:
                log.error(json.dumps(r._get("errors"), indent=4))
        log.error(f"HERE: {r.text}")
        r.raise_for_status()

    @staticmethod
    def _warn_empty_feature_stats(features: List[str]):
        if features:
            log.warning(_NO_FEATURES.format(thefeatures=', '.join(features)))

    @staticmethod
    def _file_format_suffix(fmt: FileFormat):
        if isinstance(fmt, Parquet):
            return ".parquet"
        elif isinstance(fmt, Orc):
            return ".orc"
        elif isinstance(fmt, CSV):
            return ".csv"
        else:
            raise ValueError("Unknown file format: '{f}'".format(f=type(fmt).__name__))
