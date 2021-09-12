from cnvrg.modules.cnvrg_job import CnvrgJob
from cnvrg.modules.project import Project
import cnvrg.helpers.string_helper as string_helper
import cnvrg.helpers.param_build_helper as param_build_helper
from cnvrg.helpers.env_helper import CURRENT_JOB_TYPE, CURRENT_JOB_ID, ENDPOINT, POOL_SIZE
from cnvrg.modules.errors import UserError
from cnvrg.helpers.url_builder_helper import url_join
from cnvrg.helpers.error_catcher import suppress_exception
import cnvrg.helpers.parallel_helper as parallel_helper
import cnvrg.helpers.apis_helper as apis_helper
from cnvrg.modules.dataset import Dataset
from cnvrg.modules.errors import CnvrgError
import json
import sys
import time
import os
import requests
import datetime
import traceback
import pandas as pd
import csv

from cnvrg.modules.endpoint_version_data import EndpointVersionData


class Endpoint(CnvrgJob):
    def __init__(self, endpoint=None, project=None):
        owner, project_slug, slug = param_build_helper.parse_params(endpoint, param_build_helper.ENDPOINT)

        p = Project.factory(owner, project)
        if p is None:
            p = Project(url_join(owner, project_slug))

        if not slug:
            raise UserError("Cant create an endpoint without slug")
        slug = slug or CURRENT_JOB_ID
        self.model_name = os.environ.get("CNVRG_MODEL_NAME", "unknown")
        self.log_input = self.should_log_input()
        self.log_output = self.should_log_output()

        self.project = p
        super(Endpoint, self).__init__(slug, ENDPOINT, p)
        self.__data = None

    def __base_log(self, **params):
        log = {
            "job_id": self.job_slug,
            "job_type": self.job_type,
            "owner": self.job_owner_slug,
            "project": self.job_project_slug,
            "model": self.model_name,
            "event_time": time.time(),
            **params
        }
        print(json.dumps(log))
        sys.stdout.flush()

    def log_request(self, input_params="", result="", start_time=None):
        hash = {}
        if self.log_input:
            input_str = str(input_params)
            if len(input_str) > 1000:
                print("Input was cropped due to log size (limited to 1000 chars)")
                print("full input: {}".format(input_str))
                input_str = input_str[:1000]
            hash["input"] = input_str
        else:
            hash["input"] = ""
        if self.log_output:
            output_str = str(result)
            if len(output_str) > 1000:
                print("Output was cropped due to log size (limited to 1000 chars)")
                print("full output: {}".format(output_str))
                output_str = output_str[:1000]
            hash["output"] = output_str
        else:
            hash["output"] = ""
        hash["start_time"] = str(datetime.datetime.utcfromtimestamp(int(start_time)))
        end_time = time.time()
        elapsed_time = int((end_time - start_time) * 1000)  # ms
        hash["elapsed_time"] = elapsed_time
        self.__base_log(**hash)

    def log_error(self, e, trace=False):
        hash = {}
        hash["error"] = str(e)
        if trace:
            hash["traceback"] = traceback.format_exc()
        self.__base_log(**hash)

    def log_param(self, tag_name=None, tag_value=None):
        hash = {}
        hash[tag_name] = tag_value
        hash["cnvrg_tag_name"] = tag_name
        self.__base_log(**hash)

    def log_metric(self, name=None, y:float=None, x=None):
        hash = {}
        try:
            hash[name] = float(y)
            hash["y"] = float(y)
        except Exception as e:
            print("ERROR {}".format(e), file=sys.stderr)
            return
        hash["x"] = x
        hash["cnvrg_metric_name"] = name
        self.__base_log(**hash)

    def log_prediction(self, input=None, output=None, elapsed_time=0):
        start_time = datetime.datetime.utcnow().strftime("%c")
        self.__base_log(input=input, output=output, elapsed_time=elapsed_time, start_time=start_time)

    def scale_up(self):
        return apis_helper.post_v2(
            url_join(self.project.get_base_url(api="v2"), 'endpoints', self.data["slug"], "scale_up"), data={})

    def scale_down(self):
        return apis_helper.post_v2(
            url_join(self.project.get_base_url(api="v2"), 'endpoints', self.data["slug"], "scale_down"), data={})

    def update_model(self, title=None, kind=None, input_file=None, file_name=None, function_name=None,
                     kafka_brokers=None, kafka_input_topics=None, kafka_output_topics=None, templates_names=None,
                     image_slug=None, commit=None, prep_file=None, prep_function=None, git_commit=None,
                     git_branch=None, last_deployment_commits=False):
        self._refresh_data()
        if self.data["last_deployment"] == None or self.data["status"] == "stopped":
            raise CnvrgError("Can't find last deployment")
        if self.data["deployments"][-1]["is_update"]:
            raise CnvrgError("Can't update an endpoint that is currently updating")
        if templates_names and not isinstance(templates_names, list):
            raise CnvrgError("templates_names must be in a list")
        if kafka_brokers and not isinstance(kafka_brokers, list):
            raise CnvrgError("kafka_brokers must be in a list")
        if kafka_input_topics and not isinstance(kafka_input_topics, list):
            raise CnvrgError("kafka_input_topics must be in a list")
        if kafka_output_topics and not isinstance(kafka_output_topics, list):
            raise CnvrgError("kafka_output_topics must be in a list")

        if last_deployment_commits:
            git_commit = self.data["last_deployment"]["git_commit"]
            commit = self.data["last_deployment"]["commit"]

        old_kind = self.data["kind"]
        if kind is None:
            if old_kind == "webserver":
                new_kind = 0
            elif old_kind == "kafka_stream":
                new_kind = 1
            elif old_kind == "batch":
                new_kind = 2
        else:
            new_kind = kind

        data = {
            "model": {
                "title": title or int(self.data["last_deployment"]["title"]) + 1,
                "kind": new_kind,
                "input_file": input_file or self.data["last_deployment"]["input_file"],
                "file_name": file_name or self.data["last_deployment"]["file_name"],
                "function_name": function_name or self.data["last_deployment"]["function_name"],
                "kafka_brokers": kafka_brokers or self.data["last_deployment"]["kafka_brokers"],
                "kafka_input_topics": kafka_input_topics or self.data["last_deployment"]["kafka_input_topics"],
                "kafka_output_topics": kafka_output_topics or self.data["last_deployment"]["kafka_output_topics"],
                "image_slug": image_slug or self.data["last_deployment"]["image_slug"],
                "templates_names": templates_names,
                "templates_ids": [t["id"] for t in self.data["templates"]],
                "from_deployment_slug": self.data["last_deployment"]["slug"],
                "env_setup": self.data["last_deployment"]["env_setup"],
                "commit": commit or None,
                "prep_file": prep_file or self.data["last_deployment"]["prep_file"],
                "prep_function": prep_function or self.data["last_deployment"]["prep_function"],
                "git_commit": git_commit or "latest",
                "git_branch": git_branch or self.data["last_deployment"]["git_branch"]
            }
        }
        return apis_helper.post_v2(
            url_join(self.project.get_base_url(api="v2"), 'workflows', self.data["slug"], "update_model"), data)

    def link_experiment(self):
        job_id = os.environ.get("CNVRG_JOB_ID", "unknown")
        job_type = os.environ.get("CNVRG_JOB_TYPE", "unknown")
        resp = None
        if job_type == "Experiment":
            resp = apis_helper.post_v2(
                url_join(self.project.get_base_url(api="v2"), 'endpoints', self.data["slug"], "link_experiment"),
                data={"experiment_id": job_id})
        return resp

    def is_deployment_running(self):
        resp = apis_helper.get_v2(
            url_join(self.project.get_base_url(api="v2"), 'endpoints', self.data["slug"], "is_running"))
        return resp.json().get("status")

    def rollback(self):
        resp = apis_helper.post_v2(
            url_join(self.project.get_base_url(api="v2"), 'endpoints', self.data["slug"], "rollback_model"),
            data={})
        return resp.json()

    def get_predictions(self, model_title=None):
        url = url_join(self.project.get_base_url(api="v2"), 'endpoints', self.data["slug"], "predictions")
        if model_title:
            url = url_join(url, "?model_title={model_title}".format(model_title=model_title))
        resp = apis_helper.get_v2(url)
        return resp.json()

    def run_batch_predict(self, dataset, input_file, output_file, scale: bool = True):
        if not output_file or not input_file or not dataset:
            raise CnvrgError("output_file, input_file and dataset can\'t be empty")

        try:
            endpoint_type = self.data.get("kind")
            should_scale = endpoint_type == "batch" and scale

            # fetch dataset details
            ds = Dataset(dataset)
            if ds is None:
                raise CnvrgError("Can\'t find Dataset {dataset}".format(dataset=dataset))

            ds_url = ds.get_full_url()

            self.link_experiment()

            if should_scale:
                print("Starting to scale up endpoint")
                self.scale_up()

                is_running = self.is_deployment_running()
                while not is_running:
                    print("Endpoint is not running yet, retrying in 10 seconds")
                    time.sleep(10)
                    is_running = self.is_deployment_running()
                print("Endpoint is online, starting batch prediction")

                time.sleep(20)
            else:
                is_running = self.is_deployment_running()
                if is_running:
                    print("Starting batch prediction")
                else:
                    raise CnvrgError("Endpoint is not running please send scale: True or start your endpoint")

            # Input file should be absolute path
            row_list = []
            data = pd.read_csv(input_file, header=0)
            if not data:
                raise CnvrgError("Input file is empty or invalid")
            for row in data.values:
                try:
                    r_list = row.tolist()
                    resp = self.predict(r_list)
                    row_list.append([r_list, resp.get("prediction")])
                except Exception as e:
                    raise CnvrgError(e)

            # create output file tree if not exists
            dirname = os.path.dirname(output_file)
            if dirname:
                os.makedirs(dirname, exist_ok=True)

            # Output file should be absolute path in /cnvrg
            with open(output_file, 'w') as file:
                writer = csv.writer(file)
                writer.writerow(["input", "prediction"])
                for row in row_list:
                    writer.writerow(row)

            print('Uploading {output_file} to dataset {dataset}'.format(output_file=output_file, dataset=dataset))
            os.system('cnvrg data put {url} {exported_file}'.format(url=ds_url, exported_file=output_file))

            print("Batch prediction has finished")
            if should_scale:
                print("Scaling down endpoint")
                self.scale_down()
        except Exception as e:
            if should_scale:
                self.scale_down()
            raise e

    @property
    def session(self):
        return self.__session()

    @property
    def data(self):
        if self.__data:
            return self.__data
        self._refresh_data()
        return self.__data

    @property
    def title(self):
        return self.data.get("title")

    @property
    def url(self):
        return self.data.get("endpoint_url")

    @property
    def model_url(self):
        return self.data.get("public_url")

    @property
    def model_grpc_url(self):
        return self.data.get("grpc_url")

    @property
    def min_replica(self):
        return self.data.get("min_replica")

    @property
    def max_replica(self):
        return self.data.get("max_replica")

    @property
    def active_versions(self):
        return len(self.data.get("deployments"))

    @property
    def status(self):
        return self.data.get("status")

    @suppress_exception
    def __get_endpoint(self):
        return apis_helper.get(self.__base_url()).get("endpoint")

    def __base_url(self):
        return url_join(
            self.project.get_base_url(), string_helper.to_snake_case(self.job_type) + "s", self.job_slug
        )

    def _refresh_data(self):
        self.__data = self.__get_endpoint()

    def __session(self):
        session = requests.session()
        session.headers = {
            **apis_helper.JSON_HEADERS,
            "Cnvrg-Api-Key": self.data.get("api_key")
        }
        return session

    def version(self, version):
        if 0 <= version < len(self.data.get("deployments")):
            return EndpointVersionData(self.data.get("deployments")[version])
        return EndpointVersionData(self.data.get("last_deployment"))

    def predict(self, o):
        endpoint_url = self.data.get("endpoint_url")
        if not endpoint_url:
            self._refresh_data()
            endpoint_url = self.data.get("endpoint_url")
        return self.session.post(endpoint_url, data=json.dumps({"input_params": o})).json()

    def single_batch_predict(self, o):
        prediction = self.predict(o)
        if isinstance(o, dict):
            return {**o, **prediction}
        else:
            return {"query": o, **prediction}

    def disable_log_input(self):
        self.log_input = False
        os.environ["CNVRG_ENDPOINT_LOG_INPUT"] = "false"

    def should_log_input(self):
        return os.environ.get("CNVRG_ENDPOINT_LOG_INPUT", "").lower() != "false"

    def disable_log_output(self):
        self.log_output = False
        os.environ["CNVRG_ENDPOINT_LOG_OUTPUT"] = "false"

    def should_log_output(self):
        return os.environ.get("CNVRG_ENDPOINT_LOG_OUTPUT", "").lower() != "false"
