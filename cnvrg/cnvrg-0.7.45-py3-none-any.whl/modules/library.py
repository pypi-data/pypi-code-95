from cnvrg.modules.base_module import CnvrgBase
import cnvrg.helpers.apis_helper as apis_helper
from cnvrg.modules.errors import CnvrgError
import cnvrg.helpers.export_library_helper as export_library_helper
from cnvrg.modules.project import Project
from cnvrg.helpers.param_build_helper import LIBRARY, PROJECT, parse_params
from cnvrg.helpers.url_builder_helper import url_join
from cnvrg.helpers.args_helper import args_to_string, validate_args
from cnvrg.modules.experiment import Experiment
from cnvrg.helpers.param_helper import wrap_string_to_list
from typing import List
import os
import os.path
import sys
DEFAULT_WORKING_DIR = os.path.expanduser("/cnvrg_libraries")
import importlib

class Library(CnvrgBase):
    def __init__(self, library, project=None, working_dir=None, _info=None):
        owner, library = parse_params(library, LIBRARY)
        self.__working_dir = working_dir or DEFAULT_WORKING_DIR
        try:
            self.project = Project(project)
        except CnvrgError as e:
            self.project = None

        self.__library = library
        self.__owner = apis_helper.credentials.owner
        self.__info = _info
        self.__path = None
        self.__cloned = self.__lib_loaded()
        self.model = None
        self.conn = None
        self.engine = None


    def __base_url(self):
        return url_join("users", self.__owner, "libraries", self.__library)

    @staticmethod
    def export(*paths):
        paths = [os.path.abspath(p) for p in paths]
        resp = export_library_helper.export_library(*paths)
        if resp.get("library"):
            lib_key = resp.get("library").get("key")
            return Library(lib_key)
        else:
            raise CnvrgError(resp.get("message"))

    @staticmethod
    def list():
        owner = apis_helper.credentials.owner
        lib_list = list(map(lambda x: Library(url_join(x.get('owner'), x.get("title")), _info=x), apis_helper.get(url_join("users", owner, "libraries")).get("libraries")))
        return {l.title(): l for l in lib_list}

    def info(self, force=False):
        """
        get info about this library
        :param force: to force api fetching
        :return: dict represent the library
        {clone_cmd: string,
        command: string,
        arguments: list of key: values(list),
        number_of_experiments: integer,
        description: string}
        """
        if self.__info and not force:
            return self.__info
        self.__info = self.__fetch_info()
        return self.info()

    def __fetch_info(self):
        try:
            resp = apis_helper.get(self.__base_url())
            return resp.get("library")
        except Exception as e:
            raise CnvrgError("Cant find library")

    def load(self,load_model=True,install_prerequisites=True):
        """
        load library to your local directory
        :param working_dir: path to clone the library to
        """
        info = self.info()
        lib_dir = self.__lib_path()
        os.makedirs(lib_dir, exist_ok=True)
        export_library_helper.load_library(info.get("package"), lib_dir)
        self.__path = lib_dir
        model_name = info["slug"]
        module_path = lib_dir + "/" + model_name + ".py"
        if load_model and install_prerequisites:
            try:
                self.install_prerequisites()
            except Exception as e:
                print(e)
                raise CnvrgError("Can't install prerequisites")
        if load_model and os.path.exists(module_path):
            try:
                spec = importlib.util.spec_from_file_location(model_name,
                                                              module_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                self.model = mod

            except Exception as e:
                # Not always there is a model
                pass

        return lib_dir
    def install_prerequisites(self,pip3=True,bash=True):
        lib_dir = self.__lib_path()
        # install requirements
        req_file = lib_dir + "/requirements.txt"
        prerun_file = lib_dir + "/prerun.sh"
        if os.path.exists(prerun_file):
            if bash:
                os.system("bash %s" % prerun_file)
            else:
                os.system("sh %s" % prerun_file)
        if os.path.exists(req_file):
            if pip3:
                os.system("pip3 install -r %s" % req_file)
            else:
                os.system("pip install -r %s" % req_file)

    def connect(self, **kwargs):
        if self.model is None:
            raise CnvrgError("Can't find model")
            sys.exit(1)
        self.conn,self.engine = self.model.connect(**kwargs)
    def query(self, query,commit=False, **kwargs):
        if self.model is None:
            raise CnvrgError("Can't find model")
            sys.exit(1)
        return self.model.run(conn=self.conn,query=query,commit=commit, **kwargs)
    def to_csv(self, query,filename):
        if self.model is None:
            raise CnvrgError("Can't find model")
            sys.exit(1)
        self.model.to_csv(conn=self.conn,query=query,filename=filename)
    def to_df(self, query,**kwargs):
        if self.model is None:
            raise CnvrgError("Can't find model")
            sys.exit(1)
        return self.model.to_df(conn=self.conn,query=query,**kwargs)
    def to_sql(self, df=None,table_name=None, **kwargs):
        if self.model is None:
            raise CnvrgError("Can't find model")
            sys.exit(1)
        return self.model.to_sql(df=df, conn=self.engine,table_name=table_name,  **kwargs)
    def close_connection(self):
        if self.model is None:
            raise CnvrgError("Can't find model")
            sys.exit(1)
        self.model.close_connection(conn=self.conn)
    def __default_args(self):
        return {
            "project_dir": os.path.abspath(self.project.get_working_dir()),
            "output_dir": os.path.abspath(self.project.get_output_dir())
        }

    def arguments(self):
        return self.info().get("exp_arguments")

    def __mix_args(self, args=None, with_many=True, with_defaults=True):
        args = args or {}
        #exp arguments are key: values
        library_args = self.info().get("exp_arguments") or {}
        all_args = self.__default_args() if with_defaults else {}
        all_args = {
            **all_args,
            **library_args,
            **args
        }
        if not with_many: validate_args(all_args)
        return all_args

    def run(self, compute="local", **kwargs):
        """
        Runs the library on a remote or local compute.
        :param compute: Either a string or a list of computes.
        :param kwargs: All arguments required to run te
        :return: Experiment run
        """
        compute = wrap_string_to_list(compute)
        if "local" in compute:
            return self.__run_local(**kwargs)
        else:
            return self.__run(**kwargs)



    def __run(self, title=None, project=None, compute=None, dataset=None, prerun=True, requirements=None, image=None, sync_before=None, **kwargs):
        ### mix given params with default params
        arguments = self.__mix_args(kwargs)

        ### run experiment.
        return Experiment.run(command=self.info().get("command"), arguments=arguments, library=self.__library,
                              title=title, project=project, compute=compute, dataset=dataset, prerun=prerun, requirements=requirements, image=image, sync_before=sync_before)


    def __run_local(self, title=None, project=None, sync_before=None, sync_after=None, **kwargs):
        #Load the library if needed
        if not self.__lib_loaded(): self.load()

        ### Build the command
        arguments = self.__mix_args(kwargs)
        string_args = args_to_string(arguments)
        command = "{cmd} {args}".format(cmd=self.info().get("command"), args=string_args)

        ## Run a local experiment.
        return Experiment.run(command=command, library=self.__library,  compute='local', local=True, working_directory=self.__lib_path(),
                              sync_before=sync_before, sync_after=sync_after, project=project, title=title)


    def __lib_loaded(self):
        return os.path.exists(os.path.join(self.__lib_path(), "library.yml"))


    def __lib_path(self):
        working_dir = self.__working_dir
        return os.path.join(working_dir, self.info().get("slug"))


    def __str__(self):
        return """{title}
        Description: {description}
        Arguments: {arguments}
        Command: {command}
        """.format(**{**self.info(), "arguments": args_to_string(self.info().get("arguments"))})

    def title(self):
        return url_join(self.info().get("owner"), self.info().get("title"))








