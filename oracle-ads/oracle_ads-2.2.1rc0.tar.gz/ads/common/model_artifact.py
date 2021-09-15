#!/usr/bin/env python
# -*- coding: utf-8; -*-

# Copyright (c) 2021 Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

import fnmatch
import importlib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import uuid
from enum import Enum
from importlib.util import find_spec
from pathlib import Path

import oci
import pkg_resources
import python_jsonschema_objects as pjs
import yaml
from ads.common import logger, utils
from ads.common import oci_client
from ads.common import auth as authutil
from git import InvalidGitRepositoryError, Repo
from oci.data_science.models import ModelProvenance

try:
    from yaml import CDumper as dumper
    from yaml import CLoader as loader
except:
    from yaml import Dumper as dumper
    from yaml import Loader as loader

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("ADS")

MODEL_ARTIFACT_VERSION = "3.0"


class ConflictStrategy(object):
    IGNORE = "IGNORE"
    UPDATE = "UPDATE"
    CREATE = "CREATE"


class PACK_TYPE(Enum):
    SERVICE_PACK = "data_science"
    USER_CUSTOM_PACK = "published"


class ChangesNotCommitted(Exception):
    def __init__(self, path):
        msg = f"""
            File(s) at {path} are either dirty or untracked.
            Please commit changes and then save the model, or set `ignore_pending_changes=True`.
        """
        super().__init__(msg)


class ModelArtifact(object):
    def __init__(
        self,
        artifact_dir,
        conflict_strategy=ConflictStrategy.IGNORE,
        install_libs=False,
        reload=True,
        create=False,
        progress=None,
        model_file_name="model.onnx",
        inference_conda_env=None,
        data_science_env=False,
        ignore_deployment_error=False,
    ):
        self.artifact_dir = (
            artifact_dir[:-1] if artifact_dir.endswith("/") else artifact_dir
        )
        self.model = None
        self.score = None
        self.inference_conda_env = inference_conda_env
        self.data_science_env = data_science_env
        self.ignore_deployment_error = ignore_deployment_error

        if create:
            self.progress = progress
            if "CONDA_PREFIX" in os.environ and "NB_SESSION_OCID" in os.environ:
                self._generate_runtime_yaml(model_file_name=model_file_name)
            else:
                self._generate_empty_runtime_yaml(model_file_name=model_file_name)

            self.version = MODEL_ARTIFACT_VERSION

        # This will re-install the env which the model artifact was trained in.
        if install_libs:
            self.install_requirements(conflict_strategy=conflict_strategy)
        # This will reload the Model into the env
        if reload:
            self.reload(model_file_name=model_file_name)

    def __repr__(self):
        res = "Artifact directory: %s\n" % self.artifact_dir
        res += "Contains: %s" % str(self._get_files())
        return res

    def __getattr__(self, item):
        return getattr(self.score, item)

    def __fetch_repo_details(self, training_code_info):
        repo = Repo(".", search_parent_directories=True)
        # get repository url
        if len(repo.remotes) > 0:
            repository_url = (
                repo.remotes.origin.url
                if repo.remotes.origin in repo.remotes
                else list(repo.remotes.values())[0].url
            )
        else:
            repository_url = "file://" + repo.working_dir  # no remote repo

        # get git branch
        git_branch = format(repo.active_branch)
        # get git commit
        try:
            git_commit = format(str(repo.head.commit.hexsha))
            training_code_info.GIT_COMMIT = git_commit
        except ValueError:
            # do not set commit if there isn't any
            pass

        training_code_info.GIT_REMOTE = repository_url
        training_code_info.GIT_BRANCH = git_branch
        training_code_info.ARTIFACT_DIRECTORY = self.artifact_dir
        return repo, training_code_info

    def __fetch_training_env_details(self, training_info):
        conda_prefix = os.environ.get("CONDA_PREFIX", None)
        pack_name = "NOT FOUND"
        try:
            manifest = fetch_manifest_from_conda_location(conda_prefix)
            manifest_type = manifest["type"]
            pack_name = manifest["pack_path"] if "pack_path" in manifest else None
            slug = manifest["slug"] if "slug" in manifest else ""

            if manifest_type == PACK_TYPE.USER_CUSTOM_PACK.value:
                if os.path.exists(
                    os.path.join(os.path.expanduser("~"), "conda", "config.yaml")
                ):
                    with open(
                        (os.path.join(os.path.expanduser("~"), "conda", "config.yaml"))
                    ) as conf:
                        user_config = yaml.load(conf, Loader=yaml.FullLoader)
                    pack_bucket = user_config["bucket_info"]["name"]
                    pack_namespace = user_config["bucket_info"]["namespace"]
                else:
                    logger.warn(
                        f"Cannot resolve the bucket name and namespace details for the conda environment {conda_prefix}. "
                        f"You can set these values while saving the model or run `odsc init -b *bucket-name* -n *namespace*` from the terminal and then rerun prepare step again."
                    )
            if not manifest_type or manifest_type.lower() not in [
                PACK_TYPE.USER_CUSTOM_PACK.value,
                PACK_TYPE.SERVICE_PACK.value,
            ]:
                if not self.ignore_deployment_error:
                    raise Exception(
                        f"Manifest type unknown. Manifest Type: {manifest_type}"
                    )
            if not pack_name:
                if manifest_type == PACK_TYPE.USER_CUSTOM_PACK.value:
                    if self.data_science_env:
                        raise Exception(
                            f"For published environments, assign the path of the environment on \
                                        object storage to the `inference_conda_env` parameter and False to the `data_science_env` parameter."
                        )
                    error_message = f"Pack destination is not known from the manifest file in {conda_prefix}. If it was cloned from another environment, consider publishing it before preparing the model artifact. If you wish to publish the enviroment later, you may do so and provide the details while saving the model. To publish run odsc publish -s {os.path.basename(conda_prefix)} in the terminal"
                    if self.ignore_deployment_error:
                        logger.warn(error_message)
                    else:
                        if not self.inference_conda_env:
                            logger.error(error_message)
                            logger.info(
                                "You may provide oci uri to the conda environment that you wish to use witin model deployment service if you do not want to publish the current training environment."
                            )
                            raise Exception(
                                f"Could not resolve the path in the object storage for the environment: {conda_prefix}"
                            )
                else:
                    logger.warn(
                        f"Could not resolve the object storage destination of {conda_prefix}. You may provide the correct pack name and object storage details during save time."
                    )
        except Exception as e:
            raise e
        training_info.TRAINING_ENV_SLUG = slug
        if manifest_type.lower() in [
            PACK_TYPE.USER_CUSTOM_PACK.value,
            PACK_TYPE.SERVICE_PACK.value,
        ]:
            training_info.TRAINING_ENV_TYPE = manifest_type
        if pack_name:
            training_info.TRAINING_ENV_PATH = pack_name
        training_info.TRAINING_PYTHON_VERSION = sys.version.split("|")[0].strip()
        return training_info

    def __environment_details(self, model_provenance):
        model_provenance.TRAINING_REGION = os.environ.get("NB_REGION", "NOT_FOUND")
        model_provenance.TRAINING_COMPARTMENT_OCID = os.environ.get(
            "NB_SESSION_COMPARTMENT_OCID", "NOT_FOUND"
        )
        model_provenance.TRAINING_RESOURCE_OCID = os.environ.get(
            "NB_SESSION_OCID", "NOT_FOUND"
        )
        model_provenance.PROJECT_OCID = os.environ.get("PROJECT_OCID", "NOT_FOUND")
        model_provenance.TENANCY_OCID = os.environ.get("TENANCY_OCID", "NOT_FOUND")
        model_provenance.USER_OCID = os.environ.get("USER_OCID", "NOT_FOUND")
        model_provenance.VM_IMAGE_INTERNAL_ID = os.environ.get("VM_ID", "VMIDNOTSET")
        return model_provenance

    def __fetch_runtime_schema__(self):
        schema = None
        with open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "model_artifact_schema.json"
            )
        ) as schema_file:
            schema = json.load(schema_file)

        if not schema:
            raise Exception("Cannot load schema file for generating runtime yaml")

        builder = pjs.ObjectBuilder(schema)
        ns = builder.build_classes()
        return ns

    def _generate_empty_runtime_yaml(self, model_file_name="model.onnx"):
        if self.progress:
            self.progress.update("Creating runtime.yaml configuration")
        logger.warning(
            "Generating runtime.yaml template. This file needs to be updated with valid values before saving to model catalog for a successful deployment"
        )
        content = f"""
MODEL_ARTIFACT_VERSION: '{MODEL_ARTIFACT_VERSION}'
MODEL_DEPLOYMENT:
  INFERENCE_CONDA_ENV:
    INFERENCE_ENV_SLUG: <slug of the conda pack>
    INFERENCE_ENV_TYPE: <data_science or published>
    INFERENCE_ENV_PATH: oci://<bucket-name>@<namespace>/<prefix>/<env>.tar.gz
    INFERENCE_PYTHON_VERSION: <python version>
        """
        with open(os.path.join(self.artifact_dir, "runtime.yaml"), "w") as outfile:
            outfile.write(content)

    def _generate_runtime_yaml(self, model_file_name="model.onnx"):
        if self.progress:
            self.progress.update("Creating runtime.yaml configuration")
        ns = self.__fetch_runtime_schema__()
        training_env_info = self.__fetch_training_env_details(ns.TrainingCondaEnv())
        model_provenance = self.__environment_details(ns.ModelProvenance())
        model_provenance.TRAINING_CONDA_ENV = training_env_info
        try:
            _, training_code_info = self.__fetch_repo_details(ns.TrainingCodeInfo())
            model_provenance.TRAINING_CODE = training_code_info
        except InvalidGitRepositoryError:
            pass

        if not training_env_info.TRAINING_ENV_PATH:
            logger.warning(
                "We noticed that you did not publish the conda environment in which you trained the model. Publishing the conda environment you used to train the model is optional when you save the model to the catalog. However, publishing the environment ensures that the exact training environment can be re-used later"
            )
        inference_info = ns.InferenceCondaEnv()
        if not self.inference_conda_env:
            message = f"We give you the option to specify a different inference conda environment for model deployment purposes. By default it is assumed to be the same as the conda environment used to train the model. If you wish to specify a different environment for inference purposes, please assign the path of a published or data science conda environment to the optional parameter `inference_conda_env`. "
            if (
                training_env_info.TRAINING_ENV_TYPE
                and training_env_info.TRAINING_ENV_PATH
            ):
                logger.info(message)
                inference_info.INFERENCE_ENV_SLUG = training_env_info.TRAINING_ENV_SLUG
                inference_info.INFERENCE_ENV_TYPE = training_env_info.TRAINING_ENV_TYPE
                inference_info.INFERENCE_ENV_PATH = training_env_info.TRAINING_ENV_PATH
                inference_info.INFERENCE_PYTHON_VERSION = (
                    training_env_info.TRAINING_PYTHON_VERSION
                )
        else:
            if self.inference_conda_env.startswith("oci://"):
                inference_info.INFERENCE_ENV_PATH = self.inference_conda_env
            else:
                # ToDo Verify if this is a valid slug
                pass
        model_deployment_info = None
        if inference_info.INFERENCE_ENV_PATH:
            model_deployment_info = ns.ModelDeployment()
            model_deployment_info.INFERENCE_CONDA_ENV = inference_info

        if (
            not self.inference_conda_env
            and not self.data_science_env
            and inference_info.INFERENCE_ENV_TYPE == PACK_TYPE.SERVICE_PACK.value
            and training_env_info.TRAINING_ENV_PATH == inference_info.INFERENCE_ENV_PATH
        ):
            error_message = f"The inference environment {training_env_info.TRAINING_ENV_SLUG} may have undergone changes over the course of development. You can choose to publish the current environment or set data_science_env to True in the prepare api"
            if not self.ignore_deployment_error:
                raise Exception(error_message)
            else:
                logger.warning(error_message)

        if not inference_info.INFERENCE_ENV_PATH and not self.inference_conda_env:
            error_message = f"Missing information about conda environment to use during inference in model deployment service. You can provide the oci uri of the pack that you wish to use as inference in the paramenter inference_conda_env or publish your environment by following the instruction on Environment Explorer and then run the prepare method again "
            if not self.ignore_deployment_error:
                raise Exception(error_message)
            else:
                logger.warn(error_message)

        if model_deployment_info:
            runtime_info = ns.ModelArtifactSchema(
                MODEL_ARTIFACT_VERSION=MODEL_ARTIFACT_VERSION,
                MODEL_PROVENANCE=model_provenance,
                MODEL_DEPLOYMENT=model_deployment_info,
            )
        else:
            runtime_info = ns.ModelArtifactSchema(
                MODEL_ARTIFACT_VERSION=MODEL_ARTIFACT_VERSION,
                MODEL_PROVENANCE=model_provenance,
            )

        with open(os.path.join(self.artifact_dir, "runtime.yaml"), "w") as outfile:
            outfile.write("# Model runtime environment\n")
            yaml.dump(runtime_info.as_dict(), outfile, default_flow_style=False)

    def reload(self, model_file_name=None):
        """
        Reloads files in model artifact directory
        """
        spec = importlib.util.spec_from_file_location(
            "score%s" % uuid.uuid4(), os.path.join(self.artifact_dir, "score.py")
        )
        score = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(score)
        self.score = score
        if os.path.exists(os.path.join(self.artifact_dir, "runtime.yaml")):
            if model_file_name:
                self.model = self.score.load_model(model_file_name)
            else:
                self.model = self.score.load_model()
            with open(os.path.join(self.artifact_dir, "runtime.yaml")) as runtime_file:
                runtime = yaml.load(runtime_file, Loader=yaml.FullLoader)
            self.version = runtime["MODEL_ARTIFACT_VERSION"]
            if (
                "MODEL_PROVENANCE" in runtime
                and "VM_IMAGE_INTERNAL_ID" in runtime["MODEL_PROVENANCE"]
            ):
                self.VM_ID = runtime["MODEL_PROVENANCE"]["VM_IMAGE_INTERNAL_ID"]
            # Try to get conda env
            if (
                "MODEL_PROVENANCE" in runtime
                and "TRAINING_CONDA_ENV" in runtime["MODEL_PROVENANCE"]
                and "TRAINING_ENV_SLUG"
                in runtime["MODEL_PROVENANCE"]["TRAINING_CONDA_ENV"]
            ):
                self.conda_env = runtime["MODEL_PROVENANCE"]["TRAINING_CONDA_ENV"][
                    "TRAINING_ENV_SLUG"
                ]
        elif os.path.exists(os.path.join(self.artifact_dir, "ds-runtime.yaml")):
            self.model = self.score.load_model()
            with open(
                os.path.join(self.artifact_dir, "ds-runtime.yaml")
            ) as runtime_file:
                runtime = yaml.load(runtime_file, Loader=yaml.FullLoader)
            self.version = "1.0"
            self.VM_ID = None  # get ads/mlx version?
            self.conda_env = runtime["conda-env"]
        else:
            self.model = self.score.load_model()
            self.version = "0.0"
            self.VM_ID = "UNKNOWN"
            self.conda_env = "base"
            # raise FileNotFoundError(os.path.join(self.artifact_dir, 'runtime.yaml'))

    def verify(self, input_data):
        """
        Verify a model artifact directory to be published to model catalog

        Parameters
        ----------
        input_data: str, dict, BytesIO stream
            Data to be passed into the deployed model. It can be of type json (str), a dict object, or a BytesIO stream.
            All types get converted into a UTF-8 encoded BytesIO stream and is then sent to the handler.
            Any data handling past there is done in func.py (which the user can edit). By default it looks for data
            under the keyword "input", and returns data under teh keyword "prediction"

        Returns
        -------
        output_data: the resulting prediction, formatted in the same way as the input

        Example
         --------
         input_dict = {"input": train.X[:3].to_dict()}
         model_artifact.verify(input_dict)

         * returns {"prediction": [30/4, 24.8, 30.7]} *
        """

        # Fake Context obj created for Fn Handler
        class FakeCtx:
            def SetResponseHeaders(self, headers, status_code):
                return

        ctx = FakeCtx()
        from io import BytesIO

        if type(input_data) == str:
            data = BytesIO(input_data.encode("UTF-8"))
            data_type = "json"
        elif type(input_data) == dict:
            from json import dumps

            data = BytesIO(dumps(input_data).encode("UTF-8"))
            data_type = "dict"
        elif isinstance(type(input_data), type(BytesIO)):
            data = input_data
            data_type = "BytesIO"
        else:
            raise TypeError

        sys_path = sys.path.copy()
        try:
            if self.version.split(".")[0] not in ["0", "1"]:
                sys.path.insert(0, self.artifact_dir)
            else:
                sys.path.insert(0, os.path.join(self.artifact_dir, "fn-model"))
            import func

            resp = func.handler(ctx, data)
            output_json = resp.body()
        finally:
            # Reset in case func.py messes with it
            sys.path = sys_path

        if data_type == "json":
            return output_json
        output_bstream = BytesIO(resp.body().encode("UTF-8"))
        if data_type == "BytesIO":
            return output_bstream
        else:
            from json import load

            return load(output_bstream)

    def save(
        self,
        display_name=None,
        description=None,
        project_id=None,
        compartment_id=None,
        training_script_path=None,
        ignore_pending_changes=False,
        auth=None,
    ):
        """
        Saves this model artifact in model catalog

        Parameters
        ----------
        display_name: str, optional
            Model display name
        description: str, optional
            Description for the model
        project_id: str, optional
            OCID of models' project
            If None, the default project ID `config.PROJECT_OCID` would be used
        compartment_id: str, optional
            OCID of model's compartment
            If None, the default compartment ID `config.NB_SESSION_COMPARTMENT_OCID` would be used
        training_script_path: str, optional
            The training script path is either relative to the working directory,
            or an absolute path.
        ignore_pending_changes: bool, default: False
            If True, ignore uncommitted changes and use the current head commit for provenance metadata

        auth: dict
            Default is None. The default authetication is set using `ads.set_auth` API. If you need to override the
            default, use the `ads.common.auth.api_keys` or `ads.common.auth.resource_principal` to create appropriate
            authentication signer and kwargs required to instantiate DataScienceClient object
        Returns
        -------
        model: `Model` instance

        """

        runtime_yaml_file = os.path.join(self.artifact_dir, "runtime.yaml")
        if os.path.exists(runtime_yaml_file):
            with open(runtime_yaml_file, "r") as mfile:
                runtime_prep_info = yaml.load(mfile, Loader=yaml.FullLoader)
                # runtime_info['pack-info'] = deployment_pack_info
        ns = self.__fetch_runtime_schema__()
        runtime_info = ns.ModelArtifactSchema().from_json(json.dumps(runtime_prep_info))

        training_code_info = self._training_code_info(
            ns, training_script_path, ignore_pending_changes
        )
        model_provenance_metadata = ModelProvenance(
            repository_url=str(training_code_info.GIT_REMOTE),
            git_branch=str(training_code_info.GIT_BRANCH),
            git_commit=str(training_code_info.GIT_COMMIT),
            script_dir=str(training_code_info.ARTIFACT_DIRECTORY),
            training_script=str(training_code_info.TRAINING_SCRIPT),
        )
        if hasattr(runtime_info, "MODEL_PROVENANCE") and runtime_info.MODEL_PROVENANCE:
            runtime_info.MODEL_PROVENANCE.TRAINING_CODE = training_code_info

        logger.info(model_provenance_metadata)

        from ads.catalog.model import ModelCatalog

        # handle the case where project_id and/or compartment_id is not specified by the user
        if project_id is None:
            try:
                project_id = os.environ.get("PROJECT_OCID")
            except ValueError:
                print("Please set environment variable PROJECT_OCID.")
        if compartment_id is None:
            try:
                compartment_id = os.environ.get("NB_SESSION_COMPARTMENT_OCID")
            except ValueError:
                print("Please set environment variable NB_SESSION_COMPARTMENT_OCID.")
        if os.path.exists(os.path.join(self.artifact_dir, "__pycache__")):
            shutil.rmtree(
                os.path.join(self.artifact_dir, "__pycache__"), ignore_errors=True
            )

        with open(runtime_yaml_file, "w") as mfile:
            yaml.dump(runtime_info.as_dict(), mfile, Dumper=dumper)
        try:
            return ModelCatalog(
                compartment_id=compartment_id,
                ds_client_auth=auth if auth else authutil.default_signer(),
                identity_client_auth=auth if auth else authutil.default_signer(),
            ).upload_model(
                self,
                provenance_metadata=model_provenance_metadata,
                display_name=display_name,
                description=description,
                project_id=project_id,
            )
        except oci.exceptions.RequestException as e:
            if "The write operation timed out" in str(e):
                utils.print_user_message(
                    "The save operation timed out. Try to set a longer timeout(e.g. save(timeout=600, ...)).",
                    display_type="error",
                    see_also_links=None,
                    title="Error",
                )

    def _training_code_info(
        self, ns, training_script_path=None, ignore_pending_changes=False
    ):
        try:
            repo, training_code_info = self.__fetch_repo_details(ns.TrainingCodeInfo())
        except InvalidGitRepositoryError:
            repo = None
            training_code_info = ns.TrainingCodeInfo()
        if training_script_path is not None:
            if not os.path.exists(training_script_path):
                logger.warning(
                    f"Training script {os.path.abspath(training_script_path)} does not exists."
                )
            else:
                training_script = os.path.abspath(training_script_path)
                self._assert_path_not_dirty(
                    training_script_path, repo, ignore_pending_changes
                )
                training_code_info.TRAINING_SCRIPT = training_script

        self._assert_path_not_dirty(self.artifact_dir, repo, ignore_pending_changes)
        training_code_info.ARTIFACT_DIRECTORY = os.path.abspath(self.artifact_dir)

        return training_code_info

    def _assert_path_not_dirty(self, path, repo, ignore):
        if repo is not None and not ignore:
            path_abs = os.path.abspath(path)
            if os.path.commonpath([path_abs, repo.working_dir]) == repo.working_dir:
                path_relpath = os.path.relpath(path_abs, repo.working_dir)
                if repo.is_dirty(path=path_relpath) or any(
                    [
                        os.path.commonpath([path_relpath, untracked]) == path_relpath
                        for untracked in repo.untracked_files
                    ]
                ):
                    raise ChangesNotCommitted(path_abs)

    def install_requirements(self, conflict_strategy=ConflictStrategy.IGNORE):
        """
        Install missing libraries listed in model artifact

        Parameters
        ----------
        conflict_strategy: ConflictStrategy, default: IGNORE
           Determines how to handle version conflicts between the current environment and requirements of
           model artifact
           Valid values: "IGNORE" or ConflictStrategy.IGNORE, "UPDATE" or ConflictStrategy.UPDATE
           IGNORE: Use the installed version in  case of conflict
           UPDATE: Force update dependency to the version required by model artifact in case of conflict
        """
        importlib.reload(pkg_resources)
        from pkg_resources import DistributionNotFound, VersionConflict

        if self.version.split(".")[0] not in ["0", "1"] and os.path.exists(
            Path(os.path.join(self.artifact_dir), "requirements.txt")
        ):
            requirements = (
                Path(os.path.join(self.artifact_dir), "requirements.txt")
                .read_text()
                .strip()
                .split("\n")
            )
        elif self.version.split(".")[0] in ["0", "1"] and Path(
            os.path.join(self.artifact_dir), "ds-requirements.txt"
        ):
            requirements = (
                Path(os.path.join(self.artifact_dir), "ds-requirements.txt")
                .read_text()
                .strip()
                .split("\n")
            )
        else:
            raise FileNotFoundError(
                "Could not find requirements file. Please install necessary libraries and "
                "re-construct the model artifact with install_libs=False"
            )

        version_conflicts = {}
        for requirement in requirements:
            try:
                pkg_resources.require(requirement)
            except VersionConflict as vc:
                if conflict_strategy == ConflictStrategy.UPDATE:
                    pip_install("%s%s" % (vc.req.name, vc.req.specifier), "-U")
                elif conflict_strategy == ConflictStrategy.IGNORE:
                    version_conflicts[
                        "%s==%s" % (vc.dist.key, vc.dist.parsed_version)
                    ] = "%s%s" % (vc.req.name, vc.req.specifier)
            except DistributionNotFound as dnf:
                pip_install(requirement)
                # distributions_not_found.add('%s%s' % (dnf.req.name, dnf.req.specifier))
        if len(version_conflicts) > 0:
            print(
                "\033[93m"
                + str(VersionConflictWarning(version_conflicts=version_conflicts))
                + "\033[0m"
            )

    def _get_files(self):
        if os.path.exists(os.path.join(self.artifact_dir, ".model-ignore")):
            ignore_patterns = (
                Path(os.path.join(self.artifact_dir), ".model-ignore")
                .read_text()
                .strip()
                .split("\n")
            )
        else:
            ignore_patterns = []
        file_names = []
        for root, dirs, files in os.walk(self.artifact_dir):
            for name in files:
                file_names.append(os.path.join(root, name))
            for name in dirs:
                file_names.append(os.path.join(root, name))

        for ignore in ignore_patterns:
            if not ignore.startswith("#") and ignore.strip() != "":
                matches = []
                for file_name in file_names:
                    if ignore.endswith("/"):
                        ignore = ignore[:-1] + "*"
                    if not re.search(
                        fnmatch.translate("/%s" % ignore.strip()), file_name
                    ):
                        matches.append(file_name)
                file_names = matches
        return [
            matched_file[len(self.artifact_dir) + 1 :] for matched_file in file_names
        ]


class VersionConflictWarning(object):
    def __init__(self, version_conflicts):
        self.version_conflicts = version_conflicts

    def __str__(self):
        msg = "WARNING: Version conflicts found:"
        if len(self.version_conflicts) > 0:
            for lib in self.version_conflicts:
                msg += "\nInstalled: %s, Required: %s" % (
                    lib,
                    self.version_conflicts[lib],
                )
        return msg


def pip_install(package, options="-U"):
    package = re.sub(r"<|>", "=", package.split(",")[0])
    for output in execute(["pip", "install", options, package]):
        print(output, end="")


def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def fetch_manifest_from_conda_location(env_location: str):
    """
    Convenient method to fetch manifest file from an environment.

    :param env_location: Absolute path to the environment
    :type env_location: str
    """
    manifest_location = None
    for file in os.listdir(env_location):
        if file.endswith("_manifest.yaml"):
            manifest_location = f"{env_location}/{file}"
            break
    env = {}
    if not manifest_location:
        raise Exception(
            f"Could not locate manifest file in the provided environment: {env_location}. Dir Listing - "
            f"{os.listdir(env_location)}"
        )

    with open(manifest_location) as mlf:
        env = yaml.load(mlf, Loader=yaml.FullLoader)
    manifest = env["manifest"]
    return manifest
