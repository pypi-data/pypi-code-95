from .base_module import CnvrgBase
import cnvrg.helpers.config_helper as config_helper
from cnvrg.helpers.hash_helper import hash_dir
from cnvrg.helpers.apis_helper import post as apis_post, get as apis_get, put as apis_put
import cnvrg.helpers.cnvrgignore_helper as cnvrgignore_helper
from cnvrg.helpers.url_builder_helper import url_join
import yaml
import os

class CnvrgFiles(CnvrgBase):
    def __init__(self, in_dir=False):
        self.__config = {}
        self.__working_dir = None
        self.in_dir = in_dir
        if in_dir: self.__config = config_helper.load_config(".")


    ### Need to be implemented
    def _default_config(self) -> str:
        pass

    def get_working_dir(self) -> str:
        return self.__working_dir

    def get_base_url(self) -> str:
        pass

    def __save_config(self):
        self.__config = self.__config or self._default_config()
        config_helper.save_config(self.__config, self.get_working_dir())

    def __tree_path(self):
        return os.path.join(self.get_working_dir(), '.cnvrg', 'tree.yml')


    def get_current_commit(self):
        return config_helper.load_idx(self.__working_dir).get(":commit")

    def get_current_tree(self):
        return hash_dir(self.get_working_dir())


    def _generate_tree(self):
        tree = self.get_current_tree()
        os.makedirs(os.path.dirname(self.__tree_path()), exist_ok=True)
        with open(self.__tree_path(), 'w') as f:
            yaml.dump(tree, f)

    def set_commit(self, commit_sha1):
        self.__config["commit"] = commit_sha1
        self.__save_config()


    def _set_working_dir(self, working_dir, save=False):
        self.__working_dir = working_dir
        if save: self.__save_config()



    def get_latest_tree(self):
        if not os.path.exists(self.__tree_path()):
            return {}
        os.makedirs(os.path.dirname(self.__tree_path()), exist_ok=True)
        with open(self.__tree_path(), 'r') as f:
            return yaml.safe_load(f)


    def get_storage_url(self):
        return url_join(self.get_base_url(), "client")


    def fetch_commit(self, commit_sha1=None, limit=10000, offset=0, files=None):
        commit_sha1 = commit_sha1 or "latest"
        commit = apis_get(url_join(self.get_base_url(), "commits", commit_sha1), data={"limit": limit, "offset": offset, "files": files}).get("commit")
        return commit

    def get_commit_files(self, **kwargs):
        commit_size = None
        current_offset = 0
        blobs = []
        while current_offset != commit_size:
            kwargs["offset"] = current_offset
            resp = self.fetch_commit(**kwargs)
            blobs += resp.get("blobs")
            commit_size = resp.get("files_count")
            current_offset = len(blobs)
        return blobs


    def start_commit(self, is_branch=False, force=False) -> str:
        """
        :param kwargs: force, new_branch
        :return: commit_sha1 for the new commit
        """
        commit = apis_post(url_join(self.get_base_url(), 'commits'), data={"force": force, "is_branch": is_branch, "commit_sha1": self.get_current_commit()}).get("commit")
        return commit.get("sha1")

    def end_commit(self, sha1) -> bool:
        """
        :param sha1: the sha1 of the commit we want to finish.
        :return: saved successfuly, true/false
        """
        success = apis_post(url_join(self.get_base_url(), 'commits', sha1)).get("status") == 200
        if not success: return False
        self.set_commit(sha1)
        self._generate_tree()
        self.__save_config()
        return True


    def status(self, current_tree=None, commit=None, to_commit=None, force=False, new_branch=False):
        """
        Current project Status
        :param current_tree: current tree
        :param commit: current commit
        :param to_commit: commit to downlaod
        :param force: do we force our upload
        :param new_branch: we are uploading to a new branch
        :return: {updated_on_server, updated_on_local, conflicts, deleted_conflicts, deleted_on_local, deleted_on_remote}
        """
        commit = commit or self.get_current_commit()
        current_tree = current_tree or self.get_current_tree()
        resp = apis_post(url_join(self.get_base_url(), "commits", "status"), data={"tree": current_tree, "commit": commit, "to_commit": to_commit, "ignore": list(cnvrgignore_helper.get_full_ignore(self.get_working_dir()))})
        status = resp.get("status")
        if force or new_branch:
            status["conflicts"] = []
            status["deleted_conflicts"] = []
        return status

    def upload_files(self, commit_sha1, upload_payload):
        """
        :param upload_payload: {added_files, deleted_files}
        :return: added_files mapping
        """
        return apis_put(url_join(self.get_base_url(), 'commits', commit_sha1), data=upload_payload)




    def _clone_finish(self, commit_sha1, working_dir):
        self._set_working_dir(os.path.realpath(working_dir), save=True)
        self._download_finish(commit_sha1)

    def _download_finish(self, commit_sha1):
        self.set_commit(commit_sha1)
        cnvrgignore_helper.check_cnvrgignore(self.get_working_dir())
        self._generate_tree()
        self.__save_config()

    def get_config(self):
        return self.__config

    def set_config(self, **new_config):
        self.__config = {**self.__config, **new_config}



