import yaml
import os
import tempfile
import tarfile
import cnvrg.modules.errors as errors
import cnvrg.actions.project_actions as project_actions
import cnvrg.helpers.apis_helper as apis_helper
import cnvrg.helpers.files_helper as files_helper
import cnvrg.helpers.random_helper as random_helper

DEFAULT_WORKING_DIR = os.path.expanduser("~/cnvrg_libraries")

class LibraryConfig():
    def __init__(self, working_dir):
        working_dir = working_dir or os.curdir
        self.working_dir = working_dir
        self.config_path = os.path.join(working_dir, 'library.yml')
        if not os.path.exists(self.config_path): raise errors.CnvrgError("Cant find library in directory.")
        with open(self.config_path, 'r') as f:
            self.config_yaml = yaml.load(f)
            self.__load_fields()


    def __load_fields(self):
        self.__inflate_defaults()
        self.__verify_key_exists("command", "Please enter your library command")
        self.__inflate_file("requirements.txt", "requirements")
        self.__inflate_file("readme.me", "documentation")

    def __inflate_file(self, file, key):
        fpath = os.path.join(self.working_dir, file)
        if os.path.exists(fpath):
            self.config_yaml[key] = open(fpath, 'r').read()

    def __inflate_defaults(self):
        self.config_yaml = {**{
            "title": os.path.basename(self.working_dir),
            "description": "Cnvrg Library",
            "icon": None,
            "version": "1",
            "key": os.path.basename(self.working_dir)
        }, **self.config_yaml}

    def __verify_key_exists(self, key, prompt_message=None, alternative=None):
        if key not in self.config_yaml: self.__prompt_for_key(key, prompt_message)

    def __prompt_for_key(self,key, question=None):
        answer = input(question)
        self.config_yaml[key] = answer

    def getter(self):
        return self.config_yaml



def get_config(working_dir=None):
    return LibraryConfig(working_dir).getter()

def export_library(*paths):
    tar_path = os.path.join(os.curdir, "{title}.tar".format(title=random_helper.random_string(10)))
    with tarfile.open(tar_path, "w:gz") as tar_handle:
        for path in paths:
            for file in files_helper.expand(path, [".cnvrg"]):
                file = os.path.join(path, file)
                rel_path = os.path.basename(file) if os.path.isfile(path) else os.path.relpath(file, path)
                tar_handle.add(file, arcname=rel_path)
    file = {"file": open(tar_path, "rb")}
    resp = apis_helper.send_file(apis_helper.url_join("users", apis_helper.credentials.owner, "libraries"), files=file)
    os.remove(tar_path)
    return resp


def load_library(tar_url, library_dest):
    f = apis_helper.download_raw_file(tar_url)
    with tempfile.NamedTemporaryFile() as tfile:
        tfile.write(f)
        tfile.seek(0)
        with tarfile.open(tfile.name, "r:gz") as tar_handle:
            tar_handle.extractall(library_dest)