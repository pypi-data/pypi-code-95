from cnvrg.modules.base_module import CnvrgBase
from cnvrg.modules.project import Project
import cnvrg.helpers.apis_helper as apis_helper
import cnvrg.helpers.string_helper as string_helper
import os
import cnvrg.helpers.env_helper as env_helper
import cnvrg.helpers.config_helper as config_helper
import cnvrg.helpers.time_helper as time_helper
from cnvrg.modules.errors import UserError, CnvrgError
from cnvrg.helpers.url_builder_helper import url_join
import cnvrg.helpers.files_helper as files_helper
from cnvrg.modules.storage import storage_factory


LOGS_TYPE_OUTPUT = "output"
LOGS_TYPE_ERROR = "error"
LOGS_TYPE_INFO = "info"
LOGS_TYPE_WARNING = "warning"
MAX_LOGS_PER_SEND = 400

class CnvrgJob(CnvrgBase):
    def __init__(self, slug=None, job_type=None, project=None):
        self.job_slug = slug or env_helper.CURRENT_JOB_ID
        self.job_type = job_type or env_helper.CURRENT_JOB_TYPE
        if not project:
            if not config_helper.config_type() == config_helper.CONFIG_TYPE_PROJECT:
                raise UserError(
                    "Cant create an experiment without a project, please pass a project or cd into cnvrg project dir")
            project = Project()
        self.project = project
        self.job_project_slug = project.slug
        self.job_owner_slug = project.owner


    def _base_job_url(self):
        return url_join(
            #### hackish :D
            self.project.get_base_url(),"jobs", string_helper.to_snake_case(self.job_type), self.job_slug
        )


    def send_util(self, utilization):
        apis_helper.post(url_join(self._base_job_url(), "utilization"), data=[utilization])


    def log(self, logs, log_type=LOGS_TYPE_OUTPUT):
        if isinstance(logs, str): logs = [logs]
        for i in range(0, len(logs), env_helper.MAX_LOGS_PER_SEND):
            apis_helper.post(url_join(self._base_job_url(), "log"), data={"logs": logs[i:i + env_helper.MAX_LOGS_PER_SEND], "log_level": log_type, "timestamp": time_helper.now_as_string()})


    def log_artifacts(self, files: list, target="output"):
        file_dict = {}
        for file in files:
            props = files_helper.get_file_props(file)
            ### we are uploading the file to target/file_name.
            target_path = url_join(target, props["file_name"])
            props["relative_path"] = target_path
            file_dict[target_path] = {"local_path": file, "props": props}
        resp = apis_helper.post(url_join(self._base_job_url(), "log_artifacts"),
                                data={"files": [file.get("props") for file in file_dict.values()]})
        commit_sha1 = resp.get("commit")
        if not commit_sha1: raise CnvrgError("Cant upload files")
        storage = storage_factory(self.project)
        files = resp.get("files").get("files")
        std_files = []
        for k,v in files.items():
            std_files.append({
                "local_path": file_dict.get(k).get("local_path"),
                "storage_path": v.get("path"),
                "decrypted": True
            })
        storage.upload_files(std_files)
        resp = apis_helper.post(url_join(self._base_job_url(), "log_artifacts_end"),
                                data={"commit": resp.get("commit")})
        return commit_sha1




    @staticmethod
    def current_job_sync_args(output_dir=None, **kwargs):
        options = {}
        options["job"] = env_helper.CURRENT_JOB_ID
        options["job_type"] = env_helper.CURRENT_JOB_TYPE
        options["in_exp"] = "true"
        output_dir = output_dir or env_helper.CNVRG_OUTPUT_DIR
        if output_dir: options["output_dir"] = output_dir
        options = {**options, **kwargs}
        return options


