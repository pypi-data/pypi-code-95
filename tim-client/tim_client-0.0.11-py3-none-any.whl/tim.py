from datetime import datetime
from typing import List, Union
from tim.data_sources.anomaly_detection.anomaly_detection import get_anomaly_detection_job_status, get_anomaly_detection_jobs
from tim.data_sources.anomaly_detection import build_anomaly_detection_model, execute_anomaly_detection, get_anomaly_detection, get_anomaly_detection_logs, get_anomaly_detection_model_results, get_anomaly_detection_table_results, poll_anomaly_detection_status
from pandas import DataFrame
from tim.core.credentials import Credentials
from tim.data_sources.forecast.types import ForecastJobConfiguration, ForecastResultsResponse, ExecuteForecastJobResponse, BuildForecastingModelConfiguration
from tim.data_sources.anomaly_detection.types import AnomalyDetectionJobConfiguration, AnomalyDetection, AnomalyDetectionResultsResponse, BuildAnomalyDetectionModelConfiguration, ExecuteAnomalyDetectionJobResponse
from tim.data_sources.workspace.types import Workspace
from tim.data_sources.dataset.types import Dataset, DatasetListVersion
from tim.data_sources.dataset import get_dataset, get_datasets, get_dataset_versions, get_dataset_logs, upload_csv, poll_dataset_version_status, UploadDatasetResponse, UploadCSVConfiguration
from tim.data_sources.forecast import build_forecasting_model, execute, get_forecast, get_forecast_accuracies_result, get_forecast_logs, get_forecast_model_results, get_forecast_table_results, poll_forecast_status, get_status
from tim.data_sources.use_case import create_use_case, UseCaseConfiguration
from tim.data_sources.workspace import get_workspaces
from tim.types import ExecuteResponse, Status, Id


class Tim:
  __credentials: Credentials

  def __init__(
      self,
      email: str,
      password: str,
      endpoint: str = "https://tim-platform-dev.tangent.works/api/v5",
  ):
    self.__credentials = Credentials(email, password, endpoint)

  def upload_dataset(
      self, dataset: DataFrame, configuration: UploadCSVConfiguration = UploadCSVConfiguration()
  ) -> UploadDatasetResponse:
    """Upload a dataset to the TIM repository

        Parameters
        ----------
        dataset : DataFrame
        	The dataset containing time-series data
        configuration: Dict
        	Metadata of the dataset, Optional
          Available keys are: timestampFormat, timestampColumn, decimalSeparator, name, description and samplingPeriod
        	The value of samplingPeriod is a Dict containing the keys baseUnit and value

        Returns
        -------
        id : str
        dataset : Dict | None
        	Dict when successful; None when unsuccessful
        logs : list of Dict
        """
    upload_response = upload_csv(self.__credentials, dataset, configuration)
    id = upload_response['id']

    status_result = poll_dataset_version_status(self.__credentials, id, upload_response['version']['id'])

    metadata = None
    if Status(status_result['status']).value != Status.FAILED.value:
      metadata = get_dataset(self.__credentials, id)

    logs = get_dataset_logs(self.__credentials, id)

    return UploadDatasetResponse(metadata, logs)

  def build_forecasting_model(
      self, dataset_id: str, job_configuration: Union[BuildForecastingModelConfiguration, None] = None
  ) -> str:
    """Create a forecast job in the workspace the dataset is connected to (the default workspace)

    Parameters
    ----------
    dataset_id : str
        The ID of a dataset in the TIM repository
    job_configuration : BuildForecastingModelConfiguration, Optional
        TIM Engine model building and forecasting configuration, by default None
        Available keys are: name, configuration, data

    Returns
    -------
    id : str
    """
    workspace_id = get_dataset(self.__credentials, dataset_id)['workspace']['id']

    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    use_case_configuration = UseCaseConfiguration(
        name=f'Quick Forecast - {dt_string}', workspace=Id(id=workspace_id), dataset=Id(id=dataset_id)
    )

    created_use_case_id = create_use_case(
        credentials=self.__credentials, configuration=use_case_configuration
    )['id']

    config = ForecastJobConfiguration(
        **job_configuration, useCase=Id(id=created_use_case_id)
    ) if job_configuration else ForecastJobConfiguration(useCase=Id(id=created_use_case_id))

    model = build_forecasting_model(credentials=self.__credentials, job_configuration=config)

    return model['id']

  def execute_forecast(self, forecast_job_id: str,
                       wait_to_finish: bool = True) -> Union[ExecuteForecastJobResponse, ExecuteResponse]:
    """Execute a forecast job

    Parameters
    ----------
    forecast_job_id : str
        The ID of a forecast job to execute
    wait_to_finish : bool, Optional
        Wait for all results to be calculated before returning
        If set to False, the function will return once the job has started the execution process

    Returns
    -------
    metadata : Dict | None
      Dict when successful; None when unsuccessful
    model_result : Dict | None
      Dict when successful; None when unsuccessful
    table_result : DataFrame | None
      DataFrame when successful; None when unsuccessful
    accuracies : Dict | None
      Dict when successful; None when unsuccessful
    logs : list of Dict
    """
    executed_response = execute(self.__credentials, forecast_job_id)
    if wait_to_finish is False: return executed_response

    status_result = poll_forecast_status(self.__credentials, forecast_job_id)
    metadata = model_result = table_result = accuracies = None

    if Status(status_result['status']).value != Status.FAILED.value:
      metadata = get_forecast(self.__credentials, forecast_job_id)
      model_result = get_forecast_model_results(self.__credentials, forecast_job_id)
      table_result = get_forecast_table_results(self.__credentials, forecast_job_id)
      accuracies = get_forecast_accuracies_result(self.__credentials, forecast_job_id)

    logs = get_forecast_logs(self.__credentials, forecast_job_id)

    return ExecuteForecastJobResponse(metadata, model_result, table_result, accuracies, logs)

  def get_forecast_results(self, forecast_job_id: str) -> ForecastResultsResponse:
    """Retrieve the results of a forecast job

    Parameters
    ----------
    forecast_job_id : str
        The ID of a forecast job

    Returns
    -------
    metadata : Dict | None
      Dict when successful; None when unsuccessful
    model_result : Dict | None
      Dict when successful; None when unsuccessful
    table_result : DataFrame | None
      Dict when successful; None when unsuccessful
    accuracies : Dict | None
      Dict when successful; None when unsuccessful
    logs : list of Dict
    """
    metadata = model_result = table_result = accuracies = None

    status = get_status(self.__credentials, forecast_job_id)

    if Status(status['status']).value != Status.FAILED.value:
      metadata = get_forecast(self.__credentials, forecast_job_id)
      model_result = get_forecast_model_results(self.__credentials, forecast_job_id)
      table_result = get_forecast_table_results(self.__credentials, forecast_job_id)
      accuracies = get_forecast_accuracies_result(self.__credentials, forecast_job_id)

    logs = get_forecast_logs(self.__credentials, forecast_job_id)

    return ForecastResultsResponse(metadata, model_result, table_result, accuracies, logs)

  def build_forecasting_model_and_execute(
      self,
      dataset_id: str,
      job_configuration: Union[BuildForecastingModelConfiguration, None] = None,
      wait_to_finish: bool = True
  ) -> Union[ExecuteForecastJobResponse, ExecuteResponse]:
    """Create a forecast job in the workspace the dataset is connected to (default workspace) and execute it

    Parameters
    ----------
    dataset_id : str
      The ID of a dataset in the TIM repository
    job_configuration : BuildForecastingModelConfiguration
      TIM Engine model building and forecasting configuration
      Available keys are : name, configuration, data
    wait_to_finish : bool, Optional
      Wait for all results to be calculated before returning
      If set to False, the function will return once the job has started the execution process

    Returns
    -------
    metadata : Dict | None
      Dict when successful; None when unsuccessful
    model_result : Dict | None
      Dict when successful; None when unsuccessful
    table_result : DataFrame | None
      DataFrame when successful; None when unsuccessful
    accuracies : Dict | None
      Dict when successful; None when unsuccessful
    logs : list of Dict
    """

    id = self.build_forecasting_model(dataset_id, job_configuration)
    return self.execute_forecast(id, wait_to_finish)

  def build_anomaly_detection_model(
      self, dataset_id: str, job_configuration: Union[BuildAnomalyDetectionModelConfiguration, None] = None
  ) -> str:
    """Create an anomaly detection job in the workspace the dataset is connected to (default workspace)

    Parameters
    ----------
    dataset_id : str
      The ID of a dataset in the TIM repository
    job_configuration : BuildAnomalyDetectionModelConfiguration
      TIM Engine model building and anomaly detection configuration
      Available keys are : name, configuration, data

    Returns
    -------
    id : str
    """
    workspace_id = get_dataset(self.__credentials, dataset_id)['workspace']['id']

    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    use_case_configuration = UseCaseConfiguration(
        name=f'Quick Anomaly Detection - {dt_string}',
        workspace=Id(id=workspace_id),
        dataset=Id(id=dataset_id)
    )

    created_use_case_id = create_use_case(
        credentials=self.__credentials, configuration=use_case_configuration
    )['id']

    config = AnomalyDetectionJobConfiguration(
        **job_configuration, useCase=Id(id=created_use_case_id)
    ) if job_configuration else AnomalyDetectionJobConfiguration(useCase=Id(id=created_use_case_id))

    model = build_anomaly_detection_model(credentials=self.__credentials, job_configuration=config)

    return model['id']

  def execute_anomaly_detection(self, anomaly_detection_job_id: str, wait_to_finish: bool = True
                               ) -> Union[ExecuteAnomalyDetectionJobResponse, ExecuteResponse]:
    """Execute an anomaly detection job

    Parameters
    ----------
    anomaly_detection_job_id : str
        The ID of an anomaly detection job to execute
    wait_to_finish : bool, Optional
        Wait for all results to be calculated before returning
        If set to False, the function will return once the job has started the execution process

    Returns
    -------
    metadata : Dict | None
      Dict when successful; None when unsuccessful
    model_result : Dict | None
      Dict when successful; None when unsuccessful
    table_result : DataFrame | None
      DataFrame when successful; None when unsuccessful
    logs : list of Dict
    """
    executed_response = execute_anomaly_detection(self.__credentials, anomaly_detection_job_id)
    if wait_to_finish is False: return executed_response

    status = poll_anomaly_detection_status(self.__credentials, anomaly_detection_job_id)
    metadata = model_result = table_result = None

    if Status(status['status']).value != Status.FAILED.value:
      metadata = get_anomaly_detection(self.__credentials, anomaly_detection_job_id)
      model_result = get_anomaly_detection_model_results(self.__credentials, anomaly_detection_job_id)
      table_result = get_anomaly_detection_table_results(self.__credentials, anomaly_detection_job_id)

    logs = get_anomaly_detection_logs(self.__credentials, anomaly_detection_job_id)

    return ExecuteAnomalyDetectionJobResponse(metadata, model_result, table_result, logs)

  def build_anomaly_detection_model_and_execute(
      self,
      dataset_id: str,
      job_configuration: Union[BuildAnomalyDetectionModelConfiguration, None] = None,
      wait_to_finish: bool = True
  ) -> Union[ExecuteAnomalyDetectionJobResponse, ExecuteResponse]:
    """Create an anomaly detection job in the workspace the dataset is connected to (default workspace) and execute it

    Parameters
    ----------
    dataset_id : str
      The ID of a dataset in the TIM repository
    job_configuration : BuildAnomalyDetectionModelConfiguration
      TIM Engine model building and anomaly detection configuration
      Available keys are : name, configuration, data
    wait_to_finish : bool, Optional
      Wait for all results to be calculated before returning
      If set to False, the function will return once the job has started the execution process

    Returns
    -------
    metadata : Dict | None
      Dict when successful; None when unsuccessful
    model_result : Dict | None
      Dict when successful; None when unsuccessful
    table_result : DataFrame | None
      DataFrame when successful; None when unsuccessful
    logs : list of Dict
    """

    id = self.build_anomaly_detection_model(dataset_id, job_configuration)
    return self.execute_anomaly_detection(id, wait_to_finish)

  def get_anomaly_detection_results(self, anomaly_detection_job_id: str) -> AnomalyDetectionResultsResponse:
    """Retrieve the results of an anomaly detection job

    Parameters
    ----------
    anomaly_detection_job_id : str
        The ID of an anomaly detection job

    Returns
    -------
    metadata : Dict | None
      Dict when successful; None when unsuccessful
    model_result : Dict | None
      Dict when successful; None when unsuccessful
    table_result : DataFrame | None
      Dict when successful; None when unsuccessful
    accuracies : Dict | None
      Dict when successful; None when unsuccessful
    logs : list of Dict
    """
    metadata = model_result = table_result = None

    status = get_anomaly_detection_job_status(self.__credentials, anomaly_detection_job_id)

    if Status(status['status']).value != Status.FAILED.value:
      metadata = get_anomaly_detection(self.__credentials, anomaly_detection_job_id)
      model_result = get_anomaly_detection_model_results(self.__credentials, anomaly_detection_job_id)
      table_result = get_anomaly_detection_table_results(self.__credentials, anomaly_detection_job_id)

    logs = get_anomaly_detection_logs(self.__credentials, anomaly_detection_job_id)

    return AnomalyDetectionResultsResponse(metadata, model_result, table_result, logs)

  def get_workspaces(
      self,
      offset: int = 0,
      limit: int = 10000,
      user_group_id: Union[str, None] = None,
      sort: Union[str, None] = None
  ) -> List[Workspace]:
    """Get a list of workspaces and their metadata

    Parameters
    ----------
    offset : int, optional
        Number of records to be skipped from beginning of the list, by default 0
    limit : int, optional
        Maximum number of records to be returned, by default 10000
    user_group_id : Union[str, None], optional
        User Group ID, by default None
    sort : Union[str, None], optional
        Sorting output by the chosen attribute. +/- indicates ascending/descending order, by default -createdAt
        Available values : +createdAt, -createdAt, +updatedAt, -updatedAt, +title, -title

    Returns
    -------
    workspaces : list of Dict
        Available keys for each list item (workspace) : id (str), name (str), description (str), userGroup (Dict) with id (str), isFavorite (bool), createdAt (str), createdBy (str), updatedAt (str), updatedBy (str)
    """
    return get_workspaces(self.__credentials, offset, limit, user_group_id, sort)

  def get_datasets(
      self,
      offset: int = 0,
      limit: int = 10000,
      workspace_id: Union[str, None] = None,
      sort: Union[str, None] = None
  ) -> List[Dataset]:
    """Get a list of datasets and their metadata

    Parameters
    ----------
    offset : int, optional
        Number of records to be skipped from beginning of the list, by default 0
    limit : int, optional
        Maximum number of records to be returned, by default 10000
    workspace_id : Union[str, None] = None
        Filter for specific Workspace, by default None
    sort : Union[str, None] = None
        Sorting output by the chosen attribute. +/- indicates ascending/descending order.
        Available values : +createdAt, -createdAt

    Returns
    -------
    datasets : list of Dict
        Available keys for each list item (dataset) : id (str), name (str), workspace (Dict), latestVersion (Dict), description (str), isFavorite (bool), estimatedSamplingPeriod (str), createdAt (str), createdBy (str), updatedAt (str), updatedBy (str)
        Available keys for workspace are : id (str), name (str)
        Available keys for latestVersion are : id (str), status, numberOfVariables (int), numberOfObservations (int), firstTimestamp (str), lastTimestamp (str)
        Available values for status are : Registered, Running, Finished, FinishedWithWarning, Failed, Queued
    """
    return get_datasets(self.__credentials, offset, limit, workspace_id, sort)

  def get_dataset_versions(
      self,
      id: str,
      offset: int = 0,
      limit: int = 10000,
  ) -> List[DatasetListVersion]:
    """Get a list of the versions of a dataset and their metadata

    Parameters
    ----------
    id : str
        Dataset ID
    offset : int, optional
        Number of records to be skipped from beggining of the list, by default 0
    limit : int, optional
        Maximum number of records to be returned, by default 10000

    Returns
    -------
    versions : list of Dict
        Available keys for each list item (version) : id (str), createdAt (str), status
        Available values for status are : Registered, Running, Finished, FinishedWithWarning, Failed, Queued
    """
    return get_dataset_versions(self.__credentials, id, offset, limit)

  def get_anomaly_detection_jobs(
      self,
      offset: int = 0,
      limit: int = 10000,
      experiment_id: Union[str, None] = None,
      use_case_id: Union[str, None] = None,
      type: Union[str, None] = None,
      sort: str = '-createdAt'
  ) -> List[AnomalyDetection]:
    """Get a list of all detection jobs and their metadata

    Parameters
    ----------
    offset : int, optional
        Number of records to be skipped from beggining of the list, by default 0
    limit : int, optional
        Maximum number of records to be returned, by default 10000
    experiment_id : Union[str, None], optional
        Filter for specific Experiment, by default None
    useCase_id : Union[str, None], optional
        Filter for specific Use Case, by default None
    type : Union[str, None], optional
        Filter for specific types (comma separated string), by default None
        Available values : build-model, rebuild-model, detect
    sort : str, optional
        Sorting output by the chosen attribute. +/- indicates ascending/descending order, by default '-createdAt'
        Available values : +createdAt, -createdAt, +executedAt, -executedAt, +completedAt, -completedAt, +priority, -priority

    Returns
    -------
    jobs : list of Dict
        Available keys for each list item (job) are : id (str), name (str), type (str), status (str), parentId (str), sequenceId (str), useCaseId (str), experimentId (str), dataVersionId (str), createdAt (str), completedAt (str), executedAt (str), workerVersion (float), registrationBody (Dict)
        Available keys for registrationBody are : name (str), useCaseId (str), data (Dict), configuration (Dict)
    """
    return get_anomaly_detection_jobs(
        self.__credentials, offset, limit, sort, experiment_id, use_case_id, type
    )

  @property
  def credentials(self):
    return self.__credentials
