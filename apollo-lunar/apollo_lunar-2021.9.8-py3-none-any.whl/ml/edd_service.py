from typing import Any, Dict

import os
import requests
import time

from lunar.config import Config
from lunar.lunar_client import LunarError


class EDDService:
    def __init__(self, config: Config):
        if config.RUNTIME_ENV != "EDD":
            raise LunarError(code=400, msg="EDDService is only available on EDD runtime")

        self.config = config

    def copy_file_to_s3(self, model_path: str, model_name: str, model_version: str) -> Dict[str, Any]:
        data = {
            "copy_source": model_path,
            "s3_path": f"s3://lunar-model-registry-{self.config.ENV.lower()}/{model_name}/{model_version}/",
            "user_id": os.uname()[1].split("-")[2],
        }

        response = requests.post(
            url=self.config.COPY_FILES_URL,
            json=data,
        )

        if response.status_code != 200:
            raise LunarError(code=400, msg=str(response.reason))

        result = response.json()
        if result["status"] != 200:
            raise LunarError(code=400, msg=result.get("error"))

        while True:
            response = requests.post(
                url=self.config.JOB_STATUS_URL,
                json={"job_id": result["result"]["job_id"]},
            )

            if response.status_code != 200:
                raise LunarError(code=400, msg=str(response.reason))

            job_status_result = response.json()
            if job_status_result["status"] == 200:
                if job_status_result["result"]["state"] == "Succeeded":
                    break
                elif job_status_result["result"]["state"] == "Failed":
                    raise LunarError(code=400, msg=str(job_status_result["result"]["error"]))

            time.sleep(1)

        return result

    def copy_table_to_s3(
        self,
        database_name: str,
        table_name: str,
        db_type: str,
        is_put: bool = True,
        target_name: str = None,
        partition: str = None,
    ) -> Dict[str, Any]:
        assert db_type in ["dynamodb", "docdb"], "`db_type` must be one of `dynamodb` or `docdb`"
        assert isinstance(is_put, bool)

        data = {
            "database_name": database_name,
            "table_name": table_name,
            "s3_path": f"s3://lunar-loader-{self.config.ENV.lower()}/{db_type}/{target_name if target_name else table_name}/op={'put' if is_put else 'delete'}/",
            "user_id": os.uname()[1].split("-")[2],
        }
        if partition:
            data["partition"] = partition

        response = requests.post(
            url=self.config.COPY_DATABASE_URL,
            json=data,
        )

        if response.status_code != 200:
            raise LunarError(code=400, msg=str(response.reason))

        result = response.json()
        if result["status"] != 200:
            raise LunarError(code=400, msg=result.get("error"))

        while True:
            response = requests.post(
                url=self.config.JOB_STATUS_URL,
                json={"job_id": result["result"]["job_id"]},
            )

            if response.status_code != 200:
                raise LunarError(code=400, msg=str(response.reason))

            job_status_result = response.json()
            if job_status_result["status"] == 200:
                if job_status_result["result"]["state"] == "Succeeded":
                    break
                elif job_status_result["result"]["state"] == "Failed":
                    raise LunarError(code=400, msg=str(job_status_result["result"]["error"]))

            time.sleep(1)

        return response.json()
