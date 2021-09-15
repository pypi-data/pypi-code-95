from mlplatform_lib.api_client import ApiClient, RunMode
from mlplatform_lib.dataclass.experiment.type import ExperimentType
from mlplatform_lib.dataclass.model.type import ModelStatus
from mlplatform_lib.dataclass.model import ModelPredefinedaiDto, ModelInfoDto
from mlplatform_lib.dataclass import InsertTupleObject, experiment
from mlplatform_lib.mlplatform.mlplatform_http_client import MlPlatformUserAuth
from mlplatform_lib.predefinedai.predefinedai_http_client import PredefinedAIHttpClient
import os
from typing import List, Optional
from mlplatform_lib.hyperdata import HyperdataApi
import pandas as pd


class PredefinedAIApi:
    def __init__(self, api_client: ApiClient = None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

        if api_client.run_mode == RunMode.KUBERNETES:
            self.predefinedai_client = PredefinedAIHttpClient(mlplatform_addr=os.environ["mlplatformAddr"])
            self.hyperdata_api = HyperdataApi(api_client=self.api_client)

            self.mlplatform_auth = MlPlatformUserAuth(
                project_id=self.api_client.projectId,
                user_id=self.api_client.userId,
                authorization=self.api_client.Authorization,
                authorization_type=self.api_client.authorizationType,
            )

        self.experiment_id = self.api_client.experiment_id
        self.train_id = self.api_client.train_id
        self.inference_id = self.api_client.inference_id
        self.target_do_id = os.environ["targetDoId"] if "targetDoId" in os.environ else None

    def get_models(self) -> Optional[List[ModelPredefinedaiDto]]:
        if self.api_client.run_mode == RunMode.KUBERNETES:
            return self.predefinedai_client.get_model_infos(
                experiment_id=self.api_client.experiment_id,
                train_id=self.api_client.train_id,
                auth=self.mlplatform_auth,
            )
        else:
            print("Current mode is local, Skip get_model_infos.")
            return None

    def insert_model(self, model: ModelPredefinedaiDto) -> Optional[ModelPredefinedaiDto]:
        if self.api_client.run_mode == RunMode.KUBERNETES:
            model.train_id = self.train_id
            model.status = ModelStatus.SUCCESS
            model.experiment_type = ExperimentType.PREDEFINEDAI
            return self.predefinedai_client.insert_model(
                experiment_id=self.experiment_id,
                train_id=self.train_id,
                model=model,
                auth=self.mlplatform_auth,
            )
        else:
            print("Current mode is local, Skip insert_model_info.")
            model.id = 1
            model.train_id = self.train_id
            model.status = ModelStatus.SUCCESS
            model.experiment_type = ExperimentType.PREDEFINEDAI
            return model

    def insert_model_info(self, model_id: int, model_info: ModelInfoDto) -> ModelInfoDto:
        if self.api_client.run_mode == RunMode.KUBERNETES:
            model_info.status = ModelStatus.SUCCESS
            return self.predefinedai_client.insert_model_info(
                experiment_id=self.experiment_id,
                train_id=self.train_id,
                model_id=model_id,
                model_info=model_info,
                auth=self.mlplatform_auth,
            )
        else:
            print("Current mode is local, Skip insert_visualizations.")

    def _get_inference_result_table_name(self) -> str:
        pdai_experiment_dto = self.predefinedai_client.get_experiment(
            experiment_id=self.experiment_id,
            auth=self.mlplatform_auth
        )

        return f"PREDEFINEDAI_{pdai_experiment_dto.name}_{str(pdai_experiment_dto.id)}"

    def upload_inference_csv(self, inference_csv_path: str):
        if self.api_client.run_mode == RunMode.KUBERNETES:
            # 1. check is target do exists
            inference_data = pd.read_csv(inference_csv_path)
            
            table_name = self._get_inference_result_table_name()
            self.target_do_id = self.hyperdata_api.create_inference_result(
                table_name=table_name,
                object_name=table_name,
                columns=inference_data.columns.tolist()
            )

            insert_tuple_object = InsertTupleObject(
                isTruncated="True",
                targetColNames=inference_data.columns.tolist(),
                tableData=inference_data.values.tolist()
            )

            self.hyperdata_api.hyperdata_client.insert_dataobject_tuple(
                auth=self.hyperdata_api.hyperdata_auth,
                dataobject_id=self.target_do_id,
                insert_tuple_objects=insert_tuple_object
            )

            pdai_inference_dto = self.predefinedai_client.get_inference(
                experiment_id=self.experiment_id,
                inference_id=self.inference_id,
                auth=self.mlplatform_auth
            )
            pdai_inference_dto.target_do_id = self.target_do_id
            self.predefinedai_client.update_inference(
                experiment=self.experiment_id,
                inference_predefinedai=pdai_inference_dto,
                auth=self.mlplatform_auth
            )

            os.remove(inference_csv_path)
        else:
            print("Current mode is local, Skip upload_inference_csv.")
