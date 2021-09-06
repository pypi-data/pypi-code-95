from mlflow.store.tracking.rest_store import RestStore
from mlflow.utils.rest_utils import MlflowHostCreds
from infinstor_mlflow_plugin.tokenfile import get_token
from os.path import expanduser
from os.path import sep as separator
import ast
from mlflow.entities import (
        ViewType
        )
import requests
from requests.exceptions import HTTPError
import json
from mlflow.entities.model_registry.model_version_stages import (
    get_canonical_stage,
    DEFAULT_STAGES_FOR_GET_LATEST_VERSIONS,
    STAGE_DELETED_INTERNAL,
    STAGE_ARCHIVED,
)
from mlflow.entities.model_registry.registered_model import ModelVersion, RegisteredModel
from mlflow.store.entities.paged_list import PagedList
from infinstor_mlflow_plugin.new_login import bootstrap_from_mlflow_rest

class CognitoModelVersion():
    def __init__(self, name, user_id, version, creation_timestamp, last_updated_timestamp,
            current_stage, source, run_id, status):
        self.name = name
        self.user_id = user_id
        self.version = version
        self.creation_timestamp = creation_timestamp
        self.last_updated_timestamp = last_updated_timestamp
        self.current_stage = current_stage
        self.source = source
        self.run_id = status

class TagWithProperties():
    key = None
    value = None
    def __init__(self, k, v):
        self.key = k
        self.value = v

class CognitoAuthenticatedRestStore(RestStore):
    def cognito_host_creds(self):
        tokfile = expanduser("~") + separator + '.infinstor' + separator + 'token'
        token, service = get_token(tokfile, False)
        if (self.srvc):
            return MlflowHostCreds('https://' + self.srvc['mlflowserver'] + ':443/', token=token)
        else:
            return MlflowHostCreds('https://mlflow.' + service + ':443/', token=token)

    def get_service(self):
        if (self.srvc):
            return self.srvc['mlflowserver']
        tokfile = expanduser("~") + separator + '.infinstor' + separator + 'token'
        token, service = get_token(tokfile, False)
        return 'mlflow.' + service

    def get_token_string(self):
        tokfile = expanduser("~") + separator + '.infinstor' + separator + 'token'
        token, service = get_token(tokfile, False)
        return token

    def get_headers(self):
        headers = {'Content-Type': 'application/x-amz-json-1.1'}
        if (self.get_token_string().startswith('Custom')):
            headers['Authorization'] = self.get_token_string()
        else:
            headers['Authorization'] = 'Bearer ' + self.get_token_string()
        return headers

    def _hard_delete_run(self, run_id):
        """
        Permanently delete a run (metadata and metrics, tags, parameters).
        This is used by the ``mlflow gc`` command line and is not intended to be used elsewhere.
        """
        print('_hard_delete_run: Entered. run_id=' + str(run_id))
        run = self.get_run(run_id)
        if (not run):
            print('_hard_delete_run: Error. could not find run ' + str(run_id))
            return
        runs = self.search_runs(experiment_ids=[run.info.experiment_id],
                filter_string="tags.mlflow.parentRunId = \""+run_id + "\"",
                run_view_type=ViewType.ALL)
        if (len(runs) > 0):
            print('_hard_delete_run: This run has child runs. Delete child runs first')
            print('_hard_delete_run: Here are the commands to delete the child runs:')
            for chrun in runs:
                print('  mlflow gc --backend-store-uri infinstor:/// --run-ids '
                        + str(chrun.info.run_id))
            return

        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/runs/hard-delete'

        body = dict()
        body['run_id'] = run_id

        try:
            response = requests.post(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        else:
            return

    def _get_deleted_runs(self):
        print('_get_deleted_runs: Entered')
        experiments = self.list_experiments(view_type=ViewType.ALL)
        experiment_ids = map(lambda x: x.experiment_id, experiments)
        deleted_runs = self.search_runs(
            experiment_ids=experiment_ids, filter_string="", run_view_type=ViewType.DELETED_ONLY
        )
        rv = [deleted_run.info.run_uuid for deleted_run in deleted_runs]
        print('_get_deleted_runs: runs marked as deleted=' + str(rv))
        return rv

    def get_latest_versions(self, name, stages=None):
        """
        Latest version models for each requested stage. If no ``stages`` argument is provided,
        returns the latest version for each stage.

        :param name: Registered model name.
        :param stages: List of desired stages. If input list is None, return latest versions for
                       for 'Staging' and 'Production' stages.
        :return: List of :py:class:`mlflow.entities.model_registry.ModelVersion` objects.
        """
        #print('get_latest_versions: Entered. name=' + str(name) + ', stages=' + str(stages),
        #        flush=True)
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/registered-models/get'

        try:
            response = requests.get(url, params={'name':name}, headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        respjson = json.loads(response.text)
        model = respjson['registered_model']
        staging = None
        production = None
        archived = None
        for lv in model['latest_versions']:
            if (lv['current_stage'] == 'Staging'):
                if (not staging):
                    staging = lv
                elif (int(lv['version']) > int(staging['version'])):
                    staging = lv
            elif (lv['current_stage'] == 'Production'):
                if (not production):
                    production = lv
                elif (int(lv['version']) > int(production['version'])):
                    production = lv
            elif (lv['current_stage'] == 'Archived'):
                if (not archived):
                    archived = lv
                elif (int(lv['version']) > int(archived['version'])):
                    archived = lv

        latest_versions = []
        if (staging):
            latest_versions.append(CognitoModelVersion(staging['name'],
                staging['user_id'], staging['version'], staging['creation_timestamp'],
                staging['last_updated_timestamp'], staging['current_stage'],
                staging['source'], staging['run_id'], staging['status']))
        if (production):
            latest_versions.append(CognitoModelVersion(production['name'],
                production['user_id'], production['version'], production['creation_timestamp'],
                production['last_updated_timestamp'], production['current_stage'],
                production['source'], production['run_id'], production['status']))
        if (archived):
            latest_versions.append(CognitoModelVersion(archived['name'],
                archived['user_id'], archived['version'], archived['creation_timestamp'],
                archived['last_updated_timestamp'], archived['current_stage'],
                archived['source'], archived['run_id'], archived['status']))

        if stages is None or len(stages) == 0 or stages[0] == '':
            expected_stages = set(
                [get_canonical_stage(stage) for stage in DEFAULT_STAGES_FOR_GET_LATEST_VERSIONS]
            )
        else:
            expected_stages = set([get_canonical_stage(stage) for stage in stages])
        return [mv for mv in latest_versions if mv.current_stage in expected_stages]

    def get_model_version_download_uri(self, name, version):
        #print('get_model_version_download_uri: Entered. name=' + str(name)
        #        + ', version=' + str(version), flush=True)
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/model-versions/get'

        try:
            response = requests.get(url, params={'name':name, 'version':version}, headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        respjson = json.loads(response.text)
        model_version = respjson['model_version']
        return model_version['source']

    def create_registered_model(self, name, tags=None, description=None):
        """
        Create a new registered model in backend store.

        :param name: Name of the new model. This is expected to be unique in the backend store.
        :param tags: A list of :py:class:`mlflow.entities.model_registry.RegisteredModelTag`
                     instances associated with this registered model.
        :param description: Description of the model.
        :return: A single object of :py:class:`mlflow.entities.model_registry.RegisteredModel`
                 created in the backend.
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/registered-models/create'

        body = dict()
        body['name'] = name
        if (description != None):
            body['description'] = description

        tgs = []
        if (tags != None):
            for tag in tags:
                tgs.append({'key': tag.key, 'value': tag.value})
        body['tags'] = tgs

        try:
            response = requests.post(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        regmod = response.json()['registered_model']
        return self.RegisteredModel_from_dict(regmod)

    def get_registered_model(self, name):
        """
        Get registered model instance by name.

        :param name: Registered model name.
        :return: A single :py:class:`mlflow.entities.model_registry.RegisteredModel` object.
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/registered-models/get'
        try:
            response = requests.get(url, params={'name':name}, headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        respjson = json.loads(response.text)
        regmod = respjson['registered_model']
        return self.RegisteredModel_from_dict(regmod)

    def rename_registered_model(self, name, new_name):
        """
        Rename the registered model.

        :param name: Registered model name.
        :param new_name: New proposed name.
        :return: A single updated :py:class:`mlflow.entities.model_registry.RegisteredModel` object.
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/registered-models/rename'
        body = {'name': name, 'new_name': new_name}

        try:
            response = requests.post(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        regmod = response.json()['registered_model']
        return self.RegisteredModel_from_dict(regmod)

    def delete_registered_model(self, name):
        """
        Delete the registered model.
        Backend raises exception if a registered model with given name does not exist.

        :param name: Registered model name.
        :return: None
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/registered-models/delete'

        body = dict()
        body['name'] = name
        try:
            response = requests.delete(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise

    def update_registered_model(self, name, description):
        """
        Update description of the registered model.

        :param name: Registered model name.
        :param description: New description.
        :return: A single updated :py:class:`mlflow.entities.model_registry.RegisteredModel` object.
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/registered-models/update'

        body = dict()
        body['name'] = name
        if (description):
            body['description'] = description

        try:
            response = requests.patch(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        regmod = response.json()['registered_model']
        return self.RegisteredModel_from_dict(regmod)

    def list_registered_models(self, max_results, page_token):
        """
        List of all registered models.

        :param max_results: Maximum number of registered models desired.
        :param page_token: Token specifying the next page of results. It should be obtained from
                            a ``list_registered_models`` call.
        :return: A PagedList of :py:class:`mlflow.entities.model_registry.RegisteredModel` objects
                that satisfy the search expressions. The pagination token for the next page can be
                obtained via the ``token`` attribute of the object.
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/registered-models/list'

        try:
            response = requests.get(url,
                    params={'max_results':max_results, 'page_token':page_token},
                    headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        respjson = json.loads(response.text)
        registered_models = respjson['registered_models']

        rma = []
        for regmod in registered_models:
            rma.append(self.RegisteredModel_from_dict(regmod))

        next_page_token = None
        if ('next_page_token' in respjson):
            next_page_token = respjson['next_page_token']
        return PagedList(rma, next_page_token)

    def search_registered_models(
        self, filter_string=None, max_results=None, order_by=None, page_token=None
    ):
        """
        Search for registered models in backend that satisfy the filter criteria.

        :param filter_string: Filter query string, defaults to searching all registered models.
        :param max_results: Maximum number of registered models desired.
        :param order_by: List of column names with ASC|DESC annotation, to be used for ordering
                         matching search results.
        :param page_token: Token specifying the next page of results. It should be obtained from
                            a ``search_registered_models`` call.
        :return: A PagedList of :py:class:`mlflow.entities.model_registry.RegisteredModel` objects
                that satisfy the search expressions. The pagination token for the next page can be
                obtained via the ``token`` attribute of the object.
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/registered-models/search'

        params = {}
        if (filter_string != None):
            params['filter'] = filter_string
        if (max_results != None):
            params['max_results'] = max_results
        if (order_by != None):
            params['order_by'] = order_by
        if (page_token != None):
            params['page_token'] = page_token
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        respjson = json.loads(response.text)
        registered_models = respjson['registered_models']

        rma = []
        for regmod in registered_models:
            rma.append(self.RegisteredModel_from_dict(regmod))

        next_page_token = None
        if ('next_page_token' in respjson):
            next_page_token = respjson['next_page_token']
        return PagedList(rma, next_page_token)

    def set_registered_model_tag(self, name, tag):
        """
        Set a tag for the registered model.

        :param name: Registered model name.
        :param tag: :py:class:`mlflow.entities.model_registry.RegisteredModelTag` instance to log.
        :return: None
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/registered-models/set-tag'

        body = dict()
        body['name'] = name
        body['key'] = tag.key
        body['value'] = tag.value

        try:
            response = requests.post(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise

    def delete_registered_model_tag(self, name, key):
        """
        Delete a tag associated with the registered model.

        :param name: Registered model name.
        :param key: Registered model tag key.
        :return: None
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() +'/api/2.0/mlflow/registered-models/delete-tag'
        body = dict()
        body['name'] = name
        body['key'] = key
        try:
            response = requests.delete(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise

    # Model Versions CRUD
    def create_model_version(
        self, name, source, run_id=None, tags=None, run_link=None, description=None
    ):
        """
        Create a new model version from given source and run ID.

        :param name: Registered model name.
        :param source: Source path where the MLflow model is stored.
        :param run_id: Run ID from MLflow tracking server that generated the model.
        :param tags: A list of :py:class:`mlflow.entities.model_registry.ModelVersionTag`
                     instances associated with this model version.
        :param run_link: Link to the run from an MLflow tracking server that generated this model.
        :param description: Description of the version.
        :return: A single object of :py:class:`mlflow.entities.model_registry.ModelVersion`
                 created in the backend.
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/model-versions/create'

        body = dict()
        body['name'] = name
        body['source'] = source
        if (run_id != None):
            body['run_id'] = run_id
        tgs = []
        if (tags != None):
            for tag in tags:
                tgs.append({'key': tag.key, 'value': tag.value})
        body['tags'] = tgs
        if (description != None):
            body['description'] = description

        try:
            response = requests.post(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        modvers = response.json()['model_version']
        return self.ModelVersion_from_dict(modvers)

    def set_model_version_tag(self, name, version, tag):
        """
        Set a tag for the model version.

        :param name: Registered model name.
        :param version: Registered model version.
        :param tag: :py:class:`mlflow.entities.model_registry.ModelVersionTag` instance to log.
        :return: None
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/model-versions/set-tag'

        body = dict()
        body['name'] = name
        body['version'] = version
        body['key'] = tag.key
        body['value'] = tag.value

        try:
            response = requests.post(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise

    def delete_model_version_tag(self, name, version, key):
        """
        Delete a tag associated with the model version.

        :param name: Registered model name.
        :param version: Registered model version.
        :param key: Tag key.
        :return: None
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/model-versions/delete-tag'

        body = dict()
        body['name'] = name
        body['version'] = version
        body['key'] = key

        try:
            response = requests.delete(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise

    def delete_model_version(self, name, version):
        """
        Delete model version in backend.

        :param name: Registered model name.
        :param version: Registered model version.
        :return: None
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/model-versions/delete'

        body = dict()
        body['name'] = name
        body['version'] = version

        try:
            response = requests.delete(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise

    def transition_model_version_stage(self, name, version, stage, archive_existing_versions):
        """
        Update model version stage.

        :param name: Registered model name.
        :param version: Registered model version.
        :param new_stage: New desired stage for this model version.
        :param archive_existing_versions: If this flag is set to ``True``, all existing model
            versions in the stage will be automically moved to the "archived" stage. Only valid
            when ``stage`` is ``"staging"`` or ``"production"`` otherwise an error will be raised.

        :return: A single :py:class:`mlflow.entities.model_registry.ModelVersion` object.
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() \
                + '/api/2.0/mlflow/model-versions/transition-stage'

        body = dict()
        body['name'] = name
        body['stage'] = stage
        body['version'] = version
        body['archive_existing_versions'] = archive_existing_versions

        try:
            response = requests.post(url, data=json.dumps(body), headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        modvers = response.json()['model_version']
        return self.ModelVersion_from_dict(modvers)

    def get_model_version(self, name, version):
        """
        Get the model version instance by name and version.

        :param name: Registered model name.
        :param version: Registered model version.
        :return: A single :py:class:`mlflow.entities.model_registry.ModelVersion` object.
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/model-versions/get'

        params = {}
        params['name'] = name
        params['version'] = version
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        modvers = response.json()['model_version']
        return self.ModelVersion_from_dict(modvers)

    def search_model_versions(self, filter_string):
        """
        Search for model versions in backend that satisfy the filter criteria.

        :param filter_string: A filter string expression. Currently supports a single filter
                              condition either name of model like ``name = 'model_name'`` or
                              ``run_id = '...'``.
        :return: PagedList of :py:class:`mlflow.entities.model_registry.ModelVersion`
                 objects.
        """
        headers = self.get_headers()
        url = 'https://' + self.get_service() + '/api/2.0/mlflow/model-versions/search'

        params = {}
        if (filter_string != None):
            params['filter'] = filter_string
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            raise
        except Exception as err:
            print(f'Other error occurred: {err}')
            raise
        respjson = json.loads(response.text)
        model_versions = respjson['model_versions']

        rma = []
        for modvers in model_versions:
            rma.append(self.ModelVersion_from_dict(modvers))
        return PagedList(rma, 'unused')

    def RegisteredModel_from_dict(self, regmod):
        ct = None
        dscr = None
        lu = None
        tgs = None
        if ('creation_timestamp' in regmod):
            ct = regmod['creation_timestamp']
        if ('description' in regmod):
            dscr = regmod['description']
        if ('last_updated_timestamp' in regmod):
            lu = regmod['last_updated_timestamp']
        if ('tags' in regmod):
            tgs_in = regmod['tags']
            tgs = []
            for one_tg_in in tgs_in:
                tgs.append(TagWithProperties(one_tg_in['key'], one_tg_in['value']))
        return RegisteredModel(regmod['name'], creation_timestamp=ct,
                last_updated_timestamp=lu, description=dscr,
                latest_versions=self.get_latest_versions(regmod['name']),
                tags=tgs)

    def ModelVersion_from_dict(self, modvers):
        if ('description' in modvers):
            description=modvers['description']
        else:
            description=None
        if ('run_id' in modvers):
            run_id=modvers['run_id']
        else:
            run_id=None
        if ('run_link' in modvers):
            run_link=modvers['run_link']
        else:
            run_link=None
        if ('tags' in modvers):
            tgs_in = modvers['tags']
            tgs = []
            for one_tg_in in tgs_in:
                tgs.append(TagWithProperties(one_tg_in['key'], one_tg_in['value']))
        else:
            tgs = None
        return ModelVersion(modvers['name'], modvers['version'],
                modvers['creation_timestamp'],
                last_updated_timestamp=modvers['last_updated_timestamp'],
                description=description, user_id=modvers['user_id'],
                current_stage=modvers['current_stage'], source=modvers['source'],
                run_id=run_id, status=modvers['status'], status_message=None, tags=tgs,
                run_link=run_link)

    def __init__(self, store_uri=None, artifact_uri=None):
        super().__init__(self.cognito_host_creds)
        self.srvc = bootstrap_from_mlflow_rest()
