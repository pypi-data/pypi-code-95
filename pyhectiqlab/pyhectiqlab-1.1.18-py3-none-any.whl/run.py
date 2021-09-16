import os
import sys

import pyhectiqlab
from pyhectiqlab.metrics import MetricsManager
from pyhectiqlab.settings import app_url
from pyhectiqlab.events_manager import EventsManager
from pyhectiqlab.stream import LogHandler
from pyhectiqlab.buffer import Buffer
from pyhectiqlab.watermark import Watermark
from pyhectiqlab.artifacts import SharedArtifactsManager
from pyhectiqlab.notebooks import get_notebook_file
from pyhectiqlab.utils import list_all_files_in_dir

from pyhectiqlab.mlmodels import download_mlmodel as ops_download_mlmodel
from pyhectiqlab.mlmodels import upload_mlmodel as ops_upload_mlmodel
from pyhectiqlab.datasets import download_dataset as ops_download_dataset
from pyhectiqlab.datasets import upload_dataset as ops_upload_dataset
from pyhectiqlab.mlmodels import mlmodel_info_at_path
from pyhectiqlab.datasets import dataset_info_at_path

from functools import partial, wraps
from typing import Optional
from sys import getsizeof
import packaging 
import tempfile
import logging
import shutil

class Run():
    
    def __init__(self, name: str, project: str = None, should_create_project: bool = False, dry: bool = False):
        """
        name: Run name. If a run exists with this name, you'll be attached to the existing run. Otherwise a 
            new run is created.
        project: The project name. Leave None if the user with the API key has access to a single project. 
            Otherwise, you must specify the project name.
        should_create_project: bool. If true, creates a project d if if does not exists (Admin only).
        dry: bool: If true, the run is in a dry mode (no writting).
        
        """
        self._mock = dry
        self.events_manager = EventsManager(self._mock)
        # Check the python version
        self.events_manager.compare_python_version()  

        if dry:
            print("Dry mode activated.")
            self.run_view = {"id": "null"}
            self._mock = True
            self.events_manager = EventsManager(self._mock)
            self._read_only = False
        elif self.events_manager.is_logged()==False:
            print("User not authentificated. Use `pyhectiqlab.login()` for a web prompt or `hectiqlab login` in command line.")
            self._failed_init()
        else:
            # try:
            if project is None:
                projects = self.events_manager.add_event("get_all_projects", args=(), auth=True, async_method=False)
                if len(projects["result"])==1:
                    project = projects["result"][0]["name"]
                    print(f"Connecting to project {project}.")
                    self.project_view = projects["result"][0]
                else:
                    print("User has access to multiple projects. Switching to dry mode. \n--------\nFor active mode, please use a project:")
                    for el in projects["result"]:
                        print(f"{el['name']}")
                    self._failed_init()
                    pass
            else:
                self.project_view = self.events_manager.add_event("create_project", args=(project, should_create_project), auth=True, async_method=False)
                if self.project_view is None:
                    print("Project does not exists. Dry mode activated. \n--------\nUse should_create_project=True to create a project.")
                    self._failed_init()
                    pass
                if self.project_view['status_code']==401:
                    self._failed_init()
                    pass
            if project:
                self.run_view = self.events_manager.add_event("create_run", args=(name, project), auth=True, async_method=False)
                try:
                    if self.run_view["is_new"]==False:
                        print(f"Attaching to an existing run (ID :{self.run_view['p_id']}).")
                    if self.run_view['readonly']:
                        print(f"Run is read only.")
                    self._read_only = self.run_view['readonly']
                except:
                    print("An error occured while creating the run. Switching to dry mode.")
                    self._failed_init()

                if "id" not in self.run_view:
                    print("An error occured while creating the run. Switching to dry mode.")
                    self._failed_init()

        self.name = name
        self.metrics_manager = MetricsManager(run_id=self.run_view["id"], push_method=self._push_metrics)
        self.metrics_manager.set_aggr('mean')
        self.metrics_manager.update_cache_settings(max_cache_timeout=20,
                                                    min_cache_flush_delay=5, 
                                                    max_cache_length=25)
        self.log_recorder = None
        self.logger_name = ''
        self.is_recording_logs = False
        self.logs_buffer = Buffer(push_method=self._push_logs)
        return

    def write_method(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            if self.read_only:
                print('Run is read only. No actions.')
                return
            return f(self, *args, **kwargs)
        return wrapper

    def beta(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            print('This method is still in development and can be unstable.')
            return f(self, *args, **kwargs)
        return wrapper

    def will_be_depreciated(suggested_method):
        def _method(f):
            @wraps(f)
            def wrapper(self, *args, **kwargs):
                print(f'This method will be removed in a future release. Use {suggested_method} instead.')
                return f(self, *args, **kwargs)
            return wrapper
        return _method

    def set_metrics_cache_settings(self, aggr: str = 'mean', max_cache_timeout=None, max_cache_length=None, min_cache_flush_delay=None):
        """
        Update the settings of the metrics manager.

        max_cache_timeout [int]: Time interval for flushing the cache (seconds)  (default is 20)
        max_cache_length [int]: Max number of elements before flushing the cache (default is 25)
        min_cache_flush_delay [float]: Minimum delay between to successive data send (for the same key). 
                If the number of matrix is added faster than this delay, the cache will increase to
                respect the delay. (default is 5 seconds)
        aggr [str]: The aggregate method. One of ['none', 'sum', 'max', 'mean']  (default is mean)
        """
        self.metrics_manager.set_aggr(aggr)
        self.metrics_manager.update_cache_settings(max_cache_timeout=max_cache_timeout, 
                                                    max_cache_length=max_cache_length,
                                                    min_cache_flush_delay=min_cache_flush_delay)

    def _failed_init(self):
        self.run_view = {"id": "null"}
        self._mock = True
        self.events_manager = EventsManager(self._mock)
        self._read_only = True

    @write_method
    @will_be_depreciated('add_artifact')
    def add_artifacts(self, *args, **kwargs):
        self.add_artifact(*args, **kwargs)

    @write_method
    def add_artifact(self, filepath: str, step: int = None, wait_response: bool = False):
        """Log a file as an artifacts. If a file already exists with the name, it will be overwritten.

        filepath [str] : Path to the file.
        step [int]: The optional step stamp of the artifacts.
        wait_response [bool]: Set to true to upload sync. If False, the upload is made in background.
        """
        filename = os.path.basename(filepath)
        num_bytes = os.path.getsize(filepath)
        args = (self._id, filename, filepath, num_bytes, step)
        return self.events_manager.add_event("add_artifact", args, async_method=bool(1-wait_response))

    @write_method
    def add_mlmodel_usage(self, mlmodel_name: str, version: str = None):
        """Manually log that the run is using a specific model. You don't need
        to use this method if you already use `run.download_mlmodel`.

        mlmodel_name: Name of the mlmodel
        version: Version of the mlmodel. If None, the latest version is used.
        """
        args = (self._id, mlmodel_name, version, self.project_view['id'])
        self.events_manager.add_event("log_mlmodel", args)

    @write_method
    def add_mlmodel_usage_from_dirpath(self, dirpath:str):
        """Manually log that the run is using a specific model, but where 
        the name and the version are extracted from the path of the mlmodel. You don't need
        to use this method if you already use `run.download_mlmodel`.

        dirpath: Path to the mlmodel
        """
        meta = mlmodel_info_at_path(dirpath)
        assert meta is not None, f'Could not find the mlmodel at {dirpath}'

        print(f"{meta.get('name')} - {meta.get('version')}")
        args = (self._id, meta.get('name'), meta.get('version'), self.project_view['id'])
        self.events_manager.add_event("log_mlmodel", args)
        return
        
    @write_method        
    def add_mlmodel(self, source_path: str, name: str, version: str = None, short_description: str = None,
                push_dir: bool = False):
        """Add a mlmodel.

        source_path: Path to the directory/file of the mlmodel
        name: Name of the model without spaces and backslash (e.g., 'text-model')
        version: Version in format '{major}.{minor}.{micro}' (e.g., 1.2.0). If None, 
            the version 1.0.0 is assigned or an increment of minor of the latest version of the
            model with this name (e.g. 1.3.3 -> 1.4.0)
        short_description: Short description.
        push_dir: Must be set to True if the source_path is a directory
        """
        mlmodel = ops_upload_mlmodel(source_path=source_path, 
            mlmodel_name=name,
             run_id=self._id, 
             version=version,
             short_description=short_description,
             push_dir=push_dir)
        if mlmodel is not None:
            self.add_mlmodel_usage(mlmodel.get('name'), version=mlmodel.get('version'))

    def download_mlmodel(self, mlmodel_name: str, version: str = None, save_path: str = './', overwrite:bool = False):
        """Download an existing mlmodel from the run's project.

        source_path: Path to the directory/file of the mlmodel
        mlmodel_name: Name of the model without spaces and backslash (e.g., 'text-model')
        version: Specific version of the model. If None, the latest version is fetched.
        save_path: Path to where the model is saved.
        overwrite: Set to True to overwrite in save_path.
        """
        dirpath = ops_download_mlmodel(mlmodel_name=mlmodel_name, 
                        project_id=self.project_view["id"], 
                        version=version, 
                        save_path=save_path, 
                        overwrite=overwrite)
        if dirpath is not None:
            self.add_mlmodel_usage_from_dirpath(dirpath)
        return dirpath
        
    @write_method
    def add_dataset(self, source_path: str, name: str, version: str = None, short_description: str = None,
                push_dir: bool = False):
        """Add a dataset.

        source_path: Path to the directory/file of the dataset
        name: Name of the dataset without spaces and backslash (e.g., 'text-dataset')
        version: Version in format '{major}.{minor}.{micro}' (e.g., 1.2.0). If None, 
            the version 1.0.0 is assigned or an increment of minor of the latest version of the
            dataset with this name (e.g. 1.3.3 -> 1.4.0)
        short_description: Short description.
        push_dir: Must be set to True if the source_path is a directory
        """
        dataset = ops_upload_dataset(source_path=source_path, 
            dataset_name=name,
             run_id=self._id, 
             version=version,
             short_description=short_description,
             push_dir=push_dir)
        if dataset is not None:
            self.add_dataset_usage(dataset.get('name'), version=dataset.get('version'))

    @write_method
    def add_dataset_usage(self, dataset_name: str, version: str = None):
        """Manually log that the run is using a specific dataset You don't need
        to use this method if you already use `run.download_dataset`.
    
        dataset_name: Name of the dataset
        version: Version of the dataset. If None, the latest version is used.

        """
        args = (self._id, dataset_name, version, self.project_view['id'])
        self.events_manager.add_event("log_dataset", args)

    @write_method
    def add_dataset_usage_from_dirpath(self, dirpath:str):
        """Manually log that the run is using a specific dataset. You don't need
        to use this method if you already use `run.download_dataset`.

        dirpath: Path to the mlmodel
        """
        meta = dataset_info_at_path(dirpath)
        assert meta is not None, f'Could not find the dataset at {dirpath}'

        print(f"{meta.get('name')} - {meta.get('version')}")
        args = (self._id, meta.get('name'), meta.get('version'), self.project_view['id'])
        self.events_manager.add_event("log_dataset", args)
        return

    def download_dataset(self, dataset_name: str, version: str = None, save_path: str = './', overwrite:bool = False):
        """Download an existing dataset from the run's project.

        source_path: Path to the directory/file of the dataset
        mlmodel_name: Name of the dataset without spaces and backslash (e.g., 'text-dataset')
        version: Specific version of the dataset. If None, the latest version is fetched.
        save_path: Path to where the dataset is saved.
        overwrite: Set to True to overwrite in save_path.
        """
        dirpath = ops_download_dataset(dataset_name=dataset_name, 
                        project_id=self.project_view["id"], 
                        version=version, 
                        save_path=save_path, 
                        overwrite=overwrite)
        if dirpath is not None:
            self.add_dataset_usage_from_dirpath(dirpath)   
        return dirpath
    
    @write_method
    def add_config(self, config: 'Config', prefix=""):
        """Log a config object (pyhectiqlab.Config). Use prefix 
        to log a config in a nested path.
        """
        config.push_as_meta(self, prefix=os.path.join("config/", prefix))

    @write_method
    @will_be_depreciated('add_tf_model_as_artifact')
    def add_tf_model(self, *args, **kwargs):
        """Add a tensorflow model as an artifact. This method will be depreciated. Use 
        `add_tf_model_as_artifact`
        """
        self.add_tf_model_as_artifact(*args, **kwargs)

    @write_method
    def add_tf_model_as_artifact(self, model: 'tf.keras.Model', filename: str, step: int = None):
        """Add a tensorflow model as an artifact.
        """
        save_path = tempfile.mkdtemp()
        model.save_weights(f"{save_path}/{filename}")
        p = tempfile.mkdtemp()
        shutil.make_archive(f"{p}/{filename}", 'zip', save_path)
        self.add_artifact(f"{p}/{filename}.zip", step=step)

    @write_method
    def add_directory_as_zip_artifact(self, dirpath: str, step: int = None):
        """Compress a full directory and add the compressed file as an artifact.
        """
        p = tempfile.mkdtemp()
        filename = os.path.basename(dirpath)
        shutil.make_archive(f"{p}/{filename}", 'zip', root_dir=dirpath)
        self.add_artifact(f"{p}/{filename}.zip", step=step)

    @write_method
    def add_shared_artifact(self, filename: str):
        """Push a shared artifact.
        """
        m = SharedArtifactsManager()
        m.push_artifact(filepath=filename, project_id=self.project_view["id"])

    def list_shared_artifact(self):
        """Returns a list of the shared artifacts for this project.
        """
        m = SharedArtifactsManager()
        return m.list_artifacts(project_id=self.project_view["id"])

    @write_method
    def add_metrics(self, key: 'str', value: float, step: int):
        """Add a metrics. The metrics is saved even if there already exists a value
        for the same key and step. 

        key [str]: Key used for the metrics. The format with backlash such as `metrics/train`
            will be recognized to organize the metrics.
        value [float]. If tensor, is casted to float.
        step [int]: Training step. Casted to integer.
        """
        self.metrics_manager.add(key, float(value), int(step))

    @write_method
    def add_tag(self, name: str, description: str = None, color: str = None):
        """Add tag to a run. If the tag does not already exists by this name,
        a new tag is created with the given description and color.
        """
        args = (self._id, name, description, color)
        self.events_manager.add_event("add_tag", args)

    @write_method
    def add_package_versions(self, packages: Optional[dict] =None, with_sys: bool = True, with_python: bool = True, with_git: bool = True):
        """Save the version of the imported packages.

        Usage:
        add_package_versions(globals())
        """
        water = Watermark()
        versions = {}
        if with_python:
            versions["python"] = water.get_pyversions()
        if with_sys:
            versions["system"] = water.get_sysinfo()
        if packages:
            versions["packages"] = water.get_all_import_versions(packages)
        if with_git:
            git_info = water.get_git_info()
            if git_info:
                versions["git"] = water.get_git_info()

        args = (self._id, versions)
        self.events_manager.add_event("push_package_versions", args)

    @write_method
    def add_package_repo_state(self, package: str = None):
        """Save the branch/commit/origin of the git repo in which
        a package is located.

        Example:
            self.add_package_repo_state('pyhectiqlab')
        """
        water = Watermark()
        result = water.get_repo_info(package)
        data = {package: result}
        args = (self._id, data)
        self.events_manager.add_event("push_git_package_state", args)

    @write_method
    def add_current_notebook(self, stamp: str = 'datetime'):
        """If the run is executed in a jupyter notebook, this
        will add your current notebook as an artifact.

        stamp [str]: Add a stamp on the notebook name.
                    One of 'datetime', 'date', None
        """
        filename = get_notebook_file(stamp)
        self.add_artifact(filename)

    @write_method
    def failed(self):
        """Set the run to the failed status.
        """
        args = (self._id, "failed")
        self.events_manager.add_event("set_run_status", args)

    @write_method
    def _stopped(self):
        """Set the run to the stopped status.
        """
        args = (self._id, "stopped")
        self.events_manager.add_event("set_run_status", args)
        
    @write_method
    def completed(self):
        """Set the run to the completed with success status.
        """
        args = (self._id, "completed")
        self.events_manager.add_event("set_run_status", args)
        
    @write_method
    def pending(self):
        """Set the run to the pending status.
        """
        args = (self._id, "pending")
        self.events_manager.add_event("set_run_status", args)
        
    @write_method
    def running(self):
        """Set the run to the running status.
        """
        args = (self._id, "running")
        self.events_manager.add_event("set_run_status", args)
        
    @write_method
    def training(self):
        """Set the run to the training status.
        """
        args = (self._id, "training")
        self.events_manager.add_event("set_run_status", args)
        
    @write_method
    def add_meta(self, key, value):
        """Add or update a meta information in the format of
        key/value.
        """ 
        args = (self._id, key, value)
        self.events_manager.add_event("push_meta", args)
        
    @write_method
    def set_note(self, text: str):
        """Add or update a custom note field for the run.
        """
        args = (self._id, text)
        self.events_manager.add_event("set_note", args)
    
    @write_method
    def set_paper(self, content: str):
        """Overwrite the content of the paper of the run.
        """
        args = (self._id, content)
        self.events_manager.add_event("set_paper", args)

    @write_method
    def start_recording_logs(self, logger_name=None):
        """Start tailing the logs on a logger name.
        If logger_name is None, the default __name__ will be taken and
        you may use the returned logger.
        """
        self.is_recording_logs = True
        self.logs_buffer.start(key="logs")
        
        print("Start recording logs.")
        if (self.log_recorder is None) and self.logger_name!=logger_name:
            func = partial(self.logs_buffer.add, key="logs")
            self.log_recorder = LogHandler(func)
            console  = logging.StreamHandler()  
            console.setLevel(logging.DEBUG)

            name = logger_name
            if name is None:
                name = __name__
            self.logger_name = name

            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)
            logger.addHandler(self.log_recorder)

            # Handle all exceptions
            def handle_exception(exc_type, exc_value, exc_traceback):
                if issubclass(exc_type, KeyboardInterrupt):
                    self._stopped()
                else:
                    self.add_tag(name="failed")
                    self.failed()
                    
                logger.error("Exception", exc_info=(exc_type, exc_value, exc_traceback))
                # Flush cache before leaving
                self.logs_buffer.flush_cache()
                self.metrics_manager.flush_cache()
                sys.exit(0)                
                
            sys.excepthook = handle_exception

            return logger
        else:
            return logging.getLogger(self.logger_name)
        
    @write_method
    def stop_recording_logs(self):
        """Stop recording the logs from the logger. 
        """
        self.is_recording_logs = False
        self.logs_buffer.stop(key="logs")
        
    @write_method
    def _push_logs(self, key, msg):
        if key=="logs":
            if self.is_recording_logs:
                args = (self._id, "".join(msg))
                self.events_manager.add_event("append_logs", args)
        
    @write_method
    def _push_metrics(self, key, values):
        args = (self._id, key, values)
        self.events_manager.add_event("push_metrics", args)

    @property
    def _id(self):
        return self.run_view["id"]

    @property
    def read_only(self):
        return self._read_only

    @property
    def dry_mode(self):
        return self._mock

    @property
    def action_mode(self):
        if self.dry_mode:
            return 'dry'
        if self.read_only:
            return 'read-only'
        return 'read-write'
    
    @property
    def author(self):
        author = self.run_view.get('author')
        if author is None:
            return 'Undefined'
        return author.get('firstname') + ' ' + author.get('lastname')
        
    def __str__(self):
        # print(self.run_view)
        pad = 9
        path = f"/{self.project_view['id']}/runs/{self._id}"
        return f"<Run {self.run_view['p_id']}>"\
                f"\n{'project'.ljust(pad)}: {self.project_view['name']}"\
                f"\n{'author'.ljust(pad)}: {self.author}"\
                f"\n{'mode'.ljust(pad)}: {self.action_mode}"\
                f"\n{'url'.ljust(pad)}: {app_url+path} "

    def __repr__(self):
        return self.__str__()
    