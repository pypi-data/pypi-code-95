import abc
from os import environ

import unittest
import time

import pandas as pd
from sklearn.pipeline import Pipeline

from ibm_watson_machine_learning import APIClient
from ibm_watson_machine_learning.experiment import AutoAI
from ibm_watson_machine_learning.deployment import WebService, Batch
from ibm_watson_machine_learning.workspace import WorkSpace
from ibm_watson_machine_learning.helpers.connections import DataConnection
from ibm_watson_machine_learning.experiment.autoai.optimizers import RemoteAutoPipelines
from ibm_watson_machine_learning.tests.utils import (get_wml_credentials, get_cos_credentials, get_space_id,
                                                     is_cp4d)
from ibm_watson_machine_learning.tests.utils.cleanup import space_cleanup, delete_model_deployment
from ibm_watson_machine_learning.utils.autoai.enums import PredictionType, RunStateTypes

from ibm_watson_machine_learning.tests.utils.assertions import get_and_predict_all_pipelines_as_lale, \
    validate_autoai_timeseries_experiment

from ibm_watson_machine_learning.utils.autoai.utils import chose_model_output


class AbstractTestTSAsync(abc.ABC):
    """
    The abstract tests which covers:
    - training AutoAI Forecasting model on a dataset
    - downloading all generated pipelines to lale pipeline
    In order to execute test connection definitions must be provided
    in inheriting classes.
    """

    bucket_name = environ.get('BUCKET_NAME', "wml-autoaitests-qa")
    pod_version = environ.get('KB_VERSION', None)
    space_name = environ.get('SPACE_NAME', 'regression_tests_sdk_space')

    cos_endpoint = "https://s3.us.cloud-object-storage.appdomain.cloud"
    results_cos_path = 'results_wml_autoai'

    # to be set in every child class:
    OPTIMIZER_NAME = "AutoAI forecasting test"

    SPACE_ONLY = True
    HISTORICAL_RUNS_CHECK = True

    experiment_info = dict(name=OPTIMIZER_NAME,
                           desc='test description',
                           prediction_type=PredictionType.FORECASTING,
                           prediction_columns=['species'],
                           autoai_pod_version=pod_version
                           )

    wml_client: 'APIClient' = None
    experiment: 'AutoAI' = None
    remote_auto_pipelines: 'RemoteAutoPipelines' = None
    wml_credentials = None
    cos_credentials = None
    pipeline_opt: 'RemoteAutoPipelines' = None

    cos_resource_instance_id = None
    experiment_info: dict = None

    trained_pipeline_details = None
    run_id = None
    prev_run_id = None
    data_connection = None
    results_connection = None
    train_data = None

    pipeline: 'Pipeline' = None
    lale_pipeline = None
    deployed_pipeline = None
    hyperopt_pipelines = None
    new_pipeline = None
    new_sklearn_pipeline = None
    scoring_df = None

    project_id = None
    space_id = None

    asset_id = None
    connection_id = None

    @classmethod
    def setUpClass(cls) -> None:
        """
        Load WML credentials from config.ini file based on ENV variable.
        """
        cls.wml_credentials = get_wml_credentials()
        cls.wml_client = APIClient(wml_credentials=cls.wml_credentials.copy())

        cls.cos_credentials = get_cos_credentials()
        cls.cos_endpoint = cls.cos_credentials.get('endpoint_url')
        cls.cos_resource_instance_id = cls.cos_credentials.get('resource_instance_id')

        cls.project_id = cls.wml_credentials.get('project_id')

    def test_00a_space_cleanup(self):
        space_checked = False
        while not space_checked:
            space_cleanup(self.wml_client,
                          get_space_id(self.wml_client, self.space_name,
                                       cos_resource_instance_id=self.cos_resource_instance_id),
                          days_old=7)
            space_id = get_space_id(self.wml_client, self.space_name,
                                    cos_resource_instance_id=self.cos_resource_instance_id)
            try:
                self.assertIsNotNone(space_id, msg="space_id is None")
                space_checked = True
            except AssertionError:
                space_checked = False

        AbstractTestTSAsync.space_id = space_id

        if self.SPACE_ONLY:
            self.wml_client.set.default_space(self.space_id)
        else:
            self.wml_client.set.default_project(self.project_id)

    def test_01_initialize_AutoAI_experiment__pass_credentials__object_initialized(self):

        if self.SPACE_ONLY:
            AbstractTestTSAsync.experiment = AutoAI(wml_credentials=self.wml_credentials.copy(),
                                                    space_id=self.space_id)
        else:
            AbstractTestTSAsync.experiment = AutoAI(wml_credentials=self.wml_credentials.copy(),
                                                    project_id=self.project_id)

        self.assertIsInstance(self.experiment, AutoAI, msg="Experiment is not of type AutoAI.")

    @abc.abstractmethod
    def test_02_data_reference_setup(self):
        pass

    def test_03_initialize_optimizer(self):
        AbstractTestTSAsync.experiment_info = validate_autoai_timeseries_experiment(self.experiment_info,
                                                                                    self.pod_version)

        AbstractTestTSAsync.remote_auto_pipelines = self.experiment.optimizer(**AbstractTestTSAsync.experiment_info)

        self.assertIsInstance(self.remote_auto_pipelines, RemoteAutoPipelines,
                              msg="experiment.optimizer did not return RemoteAutoPipelines object")

    def test_04_get_configuration_parameters_of_remote_auto_pipeline(self):
        parameters = self.remote_auto_pipelines.get_params()
        print(parameters)

        # TODO: params validation
        self.assertIsInstance(parameters, dict, msg='Config parameters are not a dictionary instance.')

    def test_05_fit_run_training_of_auto_ai_in_wml(self):
        AbstractTestTSAsync.trained_pipeline_details = self.remote_auto_pipelines.fit(
            training_data_reference=[self.data_connection],
            training_results_reference=self.results_connection,
            background_mode=False)

        AbstractTestTSAsync.run_id = self.trained_pipeline_details['metadata']['id']
        self.assertIsNotNone(self.data_connection.auto_pipeline_params,
                             msg='DataConnection auto_pipeline_params was not updated.')

    def test_06_get_train_data(self):
        AbstractTestTSAsync.train_data = self.remote_auto_pipelines.get_data_connections()[0].read()

        print("train data sample:")
        print(self.train_data.head())
        self.assertGreater(len(self.train_data), 0)

        AbstractTestTSAsync.scoring_df = self.train_data[self.experiment_info['prediction_columns']][
                                         :10]

    def test_07_get_run_status(self):
        status = self.remote_auto_pipelines.get_run_status()
        run_details = self.remote_auto_pipelines.get_run_details()
        self.assertEqual(status, "completed",
                         msg="AutoAI run didn't finished successfully. Status: {},\n\n Run details {}".format(status,
                                                                                                              run_details))

    def test_08_get_run_details(self):
        parameters = self.remote_auto_pipelines.get_run_details()
        import json
        print(json.dumps(self.wml_client.training.get_details(training_uid=parameters['metadata']['id']), indent=4))
        print(parameters)
        self.assertIsNotNone(parameters)

    def test_08b_get_metrics(self):
        metrics = self.wml_client.training.get_metrics(self.run_id)
        self.assertIsNotNone(metrics)

    # # GET PIPELINE FOR TS IS NOT SUPPORTED
    # def test_09_predict_using_fitted_pipeline(self):
    #     predictions = self.remote_auto_pipelines.predict(X=self.X_values)
    #     print(predictions)
    #     self.assertGreater(len(predictions), 0)

    def test_10_summary_listing_all_pipelines_from_wml(self):
        pipelines_summary = self.remote_auto_pipelines.summary()
        print(pipelines_summary.to_string())

        chosen_models_summary = pipelines_summary[pipelines_summary['Winner']]

        self.assertGreater(len(pipelines_summary), 0, msg=f"Summary is empty:\n {pipelines_summary.to_string()}")
        if 'max_number_of_estimators' in self.experiment_info and self.experiment_info:
            nb_gen_pipelines = 4 * self.experiment_info['max_number_of_estimators']
            self.assertEqual(len(pipelines_summary), nb_gen_pipelines,
                             msg=f"Incorrect pipelines in summary:\n {pipelines_summary.to_string()}")

    def test_11__get_data_connections__return_a_list_with_data_connections_with_optimizer_params(self):
        data_connections = self.remote_auto_pipelines.get_data_connections()
        self.assertIsInstance(data_connections, list, msg="There should be a list container returned")
        self.assertIsInstance(data_connections[0], DataConnection,
                              msg="There should be a DataConnection object returned")

    def test_12_get_pipeline_params_specific_pipeline_parameters(self):
        pipeline_params = self.remote_auto_pipelines.get_pipeline_details()
        print(pipeline_params)

    # GET PIPELINE FOR TS IS NOT SUPPORTED
    # ########
    # # LALE #
    # ########
    #
    # def test_13_get_pipeline__load_lale_pipeline__pipeline_loaded(self):
    #     AbstractTestTSAsync.lale_pipeline = self.remote_auto_pipelines.get_pipeline()
    #     print(f"Fetched pipeline type: {type(self.lale_pipeline)}")
    #     from lale.operators import TrainablePipeline
    #     self.assertIsInstance(self.lale_pipeline, TrainablePipeline)
    #
    # def test_14_get_all_pipelines_as_lale(self):
    #     get_and_predict_all_pipelines_as_lale(self.remote_auto_pipelines, self.X_values)

    #################################
    #        HISTORICAL RUNS        #
    #################################

    def test_15_list_historical_runs_and_get_run_ids(self):
        if not self.HISTORICAL_RUNS_CHECK:
            self.skipTest("Skipping historical runs check.")
        runs_df = self.experiment.runs(filter=self.OPTIMIZER_NAME).list()
        print(runs_df)
        self.assertIsNotNone(runs_df)
        self.assertGreater(len(runs_df), 0)

        runs_completed_df = runs_df[runs_df.state == 'completed']

        if len(runs_completed_df) > 1:
            AbstractTestTSAsync.prev_run_id = runs_completed_df.run_id.iloc[1]  # prev run_id
            print("Random historical run_id: {}".format(AbstractTestTSAsync.prev_run_id))
            self.assertIsNotNone(AbstractTestTSAsync.prev_run_id)

    def test_16_get_params_of_last_historical_run(self):
        if not self.HISTORICAL_RUNS_CHECK:
            self.skipTest("Skipping historical runs check.")

        run_params = self.experiment.runs.get_params(run_id=self.run_id)
        self.assertIn('prediction_type', run_params,
                      msg="prediction_type field not fount in run_params. Run_params are: {}".format(run_params))

        AbstractTestTSAsync.historical_opt = self.experiment.runs.get_optimizer(self.run_id)
        self.assertIsInstance(self.historical_opt, RemoteAutoPipelines,
                              msg="historical_optimizer is not type RemoteAutoPipelines. It's type of {}".format(
                                  type(self.historical_opt)))

        train_data = self.historical_opt.get_data_connections()[0].read()

    # # GET PIPELINE FOR TS IS NOT SUPPORTED
    # def test_17_get_last_historical_pipeline_and_predict_on_historical_pipeline(self):
    #     if not self.HISTORICAL_RUNS_CHECK:
    #         self.skipTest("Skipping historical runs check.")
    #
    #     print("Getting pipeline for last run_id={}".format(self.run_id))
    #     summary = self.historical_opt.summary()
    #     pipeline_name = summary.index.values[0]
    #     historical_pipeline = self.historical_opt.get_pipeline(pipeline_name,
    #                                                            astype=self.experiment.PipelineTypes.SKLEARN)
    #     print(type(historical_pipeline))
    #     predictions = historical_pipeline.predict(self.X_values)
    #     print(predictions)
    #     self.assertGreater(len(predictions), 0, msg="Empty predictions")

    ###########################################################
    #      DEPLOYMENT SECTION    tests numbers start from 31  #
    ###########################################################

    def test_31_deployment_setup_and_preparation(self):
        # note: if target_space_id is not set, use the space_id
        if self.target_space_id is None:
            AbstractTestTSAsync.target_space_id = self.space_id
        else:
            AbstractTestTSAsync.target_space_id = self.target_space_id
        # end note

        self.wml_client.set.default_space(AbstractTestTSAsync.target_space_id)
        delete_model_deployment(self.wml_client, deployment_name=self.DEPLOYMENT_NAME)

        if self.SPACE_ONLY:
            AbstractTestTSAsync.service = WebService(source_wml_credentials=self.wml_credentials,
                                                     source_space_id=self.space_id,
                                                     target_wml_credentials=self.wml_credentials,
                                                     target_space_id=self.target_space_id)
        else:
            AbstractTestTSAsync.service = WebService(source_wml_credentials=self.wml_credentials,
                                                     source_project_id=self.project_id,
                                                     target_wml_credentials=self.wml_credentials,
                                                     target_space_id=self.target_space_id)

        self.assertIsInstance(AbstractTestTSAsync.service, WebService, msg="Deployment is not of WebService type.")
        self.assertIsInstance(AbstractTestTSAsync.service._source_workspace, WorkSpace,
                              msg="Workspace set incorrectly.")
        self.assertEqual(AbstractTestTSAsync.service.id, None, msg="Deployment ID initialized incorrectly")
        self.assertEqual(AbstractTestTSAsync.service.name, None, msg="Deployment name initialized incorrectly")

    def test_32__deploy__deploy_best_computed_pipeline_from_autoai_on_wml(self):
        best_pipeline = self.remote_auto_pipelines.summary()._series['Enhancements'].keys()[0]
        print('Deploying', best_pipeline)
        AbstractTestTSAsync.service.create(
            experiment_run_id=self.remote_auto_pipelines._engine._current_run_id,
            model=best_pipeline,
            deployment_name=self.DEPLOYMENT_NAME)

        self.assertIsNotNone(AbstractTestTSAsync.service.id, msg="Online Deployment creation - missing id")
        self.assertIsNotNone(AbstractTestTSAsync.service.name, msg="Online Deployment creation - name not set")
        self.assertIsNotNone(AbstractTestTSAsync.service.scoring_url,
                             msg="Online Deployment creation - mscoring url  missing")

    def test_33_score_deployed_model_with_empty_payload(self):
        predictions = AbstractTestTSAsync.service.score(payload=pd.DataFrame())
        print(predictions)
        self.assertIsNotNone(predictions)

        forecast_window = self.experiment_info.get('forecast_window', 1)
        self.assertEqual(len(predictions['predictions'][0]['values']), forecast_window)
        self.assertEqual(len(predictions['predictions'][0]['values'][0]),
                         len(self.experiment_info.get('prediction_columns', [])))

    def test_34_score_deployed_model_with_df(self):
        predictions = AbstractTestTSAsync.service.score(payload=self.scoring_df)
        print(predictions)
        self.assertIsNotNone(predictions)

        forecast_window = self.experiment_info.get('forecast_window', 1)
        self.assertEqual(len(predictions['predictions'][0]['values']), forecast_window)
        self.assertEqual(len(predictions['predictions'][0]['values'][0]),
                         len(self.experiment_info.get('prediction_columns', [])))

    def test_35_list_deployments(self):
        AbstractTestTSAsync.service.list()
        params = AbstractTestTSAsync.service.get_params()
        print(params)
        self.assertIsNotNone(params)

        self.assertIn(AbstractTestTSAsync.service.deployment_id, params)

    def test_36_delete_deployment(self):
        print("Delete current deployment: {}".format(AbstractTestTSAsync.service.deployment_id))
        AbstractTestTSAsync.service.delete()
        self.wml_client.repository.delete(AbstractTestTSAsync.service.asset_id)
        self.assertEqual(AbstractTestTSAsync.service.id, None, msg="Deployment ID deleted incorrectly")
        self.assertEqual(AbstractTestTSAsync.service.name, None, msg="Deployment name deleted incorrectly")
        self.assertEqual(AbstractTestTSAsync.service.scoring_url, None,
                         msg="Deployment scoring_url deleted incorrectly")
