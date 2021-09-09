import os
import json
import mimetypes

from cnvrg.helpers.apis_helper import post as apis_post, get as apis_get, credentials
from cnvrg.modules.cnvrg_files import CnvrgFiles
from cnvrg.modules.errors import CnvrgError, APINotFound
from cnvrg.helpers.url_builder_helper import url_join
from cnvrg.helpers.error_catcher import suppress_exception
from cnvrg.modules.storage.file_uploader import FileUploader, filter_by_mimetypes

import cnvrg.helpers.config_helper as config_helper
import cnvrg.helpers.env_helper as env_helper
import cnvrg.helpers.args_helper as args_helper
import cnvrg.helpers.param_build_helper as param_build_helper
import cnvrg.helpers.apis_helper as apis_helper
import cnvrg.helpers.spawn_helper as spawn_helper


class Project(CnvrgFiles):
    def __init__(self, project=None, project_url=None, working_dir=None):
        if project_url:
            owner_slug, project_slug = Project.get_owner_and_project_from_url(project_url)
        else:
            owner_slug, project_slug = param_build_helper.parse_params(project, param_build_helper.PROJECT, working_dir=working_dir)
        self.__owner = owner_slug or credentials.owner
        self.__project = project_slug

        in_dir = config_helper.is_in_dir(config_helper.CONFIG_TYPE_PROJECT, project_slug, working_dir)
        super(Project, self).__init__(in_dir=in_dir)
        if in_dir:
            self._set_working_dir(config_helper.find_config_dir(path=working_dir))
            self.in_dir = True
        elif not self.__project or not self.__owner:
            raise CnvrgError("Cant init project without params and outside project directory")

    def __fetch_config(self):
        resp = apis_get(self.get_base_url())
        return {"slug": self.slug, "owner": self.owner, **json.loads(resp.get("result"))}

    def is_git(self):
        resp = apis_get(url_join(self.get_base_url(), 'get_project'))
        if not resp.get("result"):
            return False
        result = json.loads(resp.get("result"))
        return result.get("git")

    def put_files(self, paths=None, pattern="*", message="SDK Commit", depth=False, payload=None, prefix=None, filters=None, tag_images=False):
        if not paths:
            raise CnvrgError("Please send files or path")

        full_paths = []

        for p in paths:
            is_absolute = os.path.isabs(p)
            is_dir = os.path.isdir(p)
            is_file = os.path.isfile(p)

            if is_dir:
                full_paths += FileUploader.get_files_and_dirs_recursive(root_dir=p, regex=pattern, filters=filters)
            elif is_file and filter_by_mimetypes(filters, p):
                trees = FileUploader.get_recursive_tree(p, is_absolute, is_dir, depth)
                full_paths += trees
                if not is_absolute:
                    if is_dir:
                        file_path = "{}/".format(p)
                    else:
                        file_path = p
                    full_paths.append(file_path)

                if is_absolute and depth:
                    if is_dir:
                        file_path = "{}/".format(p)
                    else:
                        file_path = p
                    full_paths.append(file_path)
            else:
                print("{} not exists skipping it".format(p))
                try:
                    paths.remove(p)
                except ValueError:
                    pass

        full_paths_set = set(full_paths) - {"./", ".", "/", "//"}
        unique_full_paths = list(full_paths_set)

        if not unique_full_paths:
            print("Nothing to upload\nAborting")
            exit(0)

        fu = FileUploader(self)
        workflow_slug = payload.get('workflow_slug', '') if payload else ''
        commit_sha1 = self.start_commit_new(message=message, payload=payload, workflow_slug=workflow_slug)
        fu.upload_multiple_files(self, files=unique_full_paths, commit_sha1=commit_sha1, prefix=prefix)
        resp = self.end_commit_new(commit_sha1=commit_sha1, tag_images=tag_images, workflow_slug=workflow_slug)
        if not resp.get("data") and not resp.get("result"):
            raise CnvrgError("Couldn’t create commit")
        else:
            sha1 = resp.get("data").get("attributes").get("sha1") if resp.get("data") else resp.get("result").get("commit_id")
            print("Successfully created commit {}".format(sha1))

    def start_commit_new(self, message="SDK Commit", payload=None, workflow_slug=''):
        if workflow_slug:
            return self.start_workflow_commit_new(message, payload, workflow_slug)
        else:
            return self.start_project_commit_new(message, payload)

    def end_commit_new(self, commit_sha1, tag_images, workflow_slug=''):
        if workflow_slug:
            return self.end_workflow_commit_new(commit_sha1, tag_images, workflow_slug)
        else:
            return self.end_project_commit_new(commit_sha1)

    def start_workflow_commit_new(self, message="SDK Commit", payload=None, workflow_slug=''):
        if payload is None:
            payload = {}

        resp = apis_helper.post_v2(
            url_join(self.owner, 'projects', self.get_project_name(), 'workflows', workflow_slug, "commits"), data={
                "job_slug": workflow_slug,
                "message": message,
                "source": "sdk-old",
                **payload
            })
        if resp.status_code == 404:
            raise APINotFound("API Not Found")

        return resp.json().get('data').get('attributes').get('sha1')

    def start_project_commit_new(self, message="SDK Commit", payload=None):
        if payload is None:
            payload = {}

        resp = apis_helper.post_v2(url_join(self.owner, "files", "start_commit"), data={
            "fileable_type": "Project",
            "fileable_slug": self.get_project_name(),
            "message": message,
            **payload
        })

        if resp.status_code == 404:
            raise APINotFound("API Not Found")

        return resp.json().get("result").get("commit_sha1")

    def end_workflow_commit_new(self, commit_sha1, tag_images, workflow_slug=''):
        resp = apis_helper.put_v2(
            url_join(self.owner, 'projects', self.get_project_name(), 'workflows', workflow_slug, "commits",commit_sha1, "end_commit"),
            data={
                "tag_images": tag_images,
            })

        return resp.json()

    def end_project_commit_new(self, commit_sha1):
        resp = apis_helper.post_v2(url_join(self.owner, "files", "end_commit"), data={
            "fileable_type": "Project",
            "fileable_slug": self.get_project_name(),
            "source": "sdk-old",
            "commit": commit_sha1
        })

        return resp.json()

    @staticmethod
    @suppress_exception
    def list(owner=None):
        owner_slug = owner or credentials.owner
        projects = []
        resp = apis_helper.get_v2(url_join(owner_slug, "projects") + '?page[size]=-1')
        for proj in resp.json()["data"]:
            slug = proj["attributes"]["slug"]
            projects.append(Project("{}/{}".format(owner_slug, slug)))
        return projects

    @staticmethod
    @suppress_exception
    def create(title, owner=None):
        owner_slug = owner or credentials.owner
        resp = apis_helper.post_v2(url_join(owner_slug, "projects"), data={"title": title})
        status = resp.status_code
        if status == 200:
            slug = resp.json()["data"]["attributes"]["slug"]
            print("Project {} created successfully".format(slug))
            return Project(slug)
        else:
            print("Could not create project")

    @staticmethod
    def factory(owner, project):
        if isinstance(project, str):
            return Project(url_join(owner, project))
        elif isinstance(project, Project):
            return project

    @property
    def owner(self):
        return self.__owner

    @property
    def slug(self):
        return self.__project

    @property
    def git(self):
        config = self.get_config()
        if config:
            return config.get(":git") or False
        return self.__fetch_config().get("git")

    def get_git_commit(self):
        return spawn_helper.run_and_get_output("git rev-parse --verify HEAD")

    def get_git_branch(self):
        return spawn_helper.run_and_get_output("git rev-parse --abbrev-ref HEAD")

    def get_base_url(self, api="v1"):
        if api == "v1":
            return "users/{owner}/projects/{project}".format(owner=self.__owner, project=self.__project)
        else:
            return "{owner}/projects/{project}".format(owner=self.__owner, project=self.__project)

    def _default_config(self):
        return {
            "project": self.__project,
            "owner": self.__owner,
            "commit": None
        }

    def web_url(self):
        return url_join(credentials.web_url(), self.__owner, 'projects', self.__project)

    def get_project_name(self):
        return self.__project.lower()

    def get_output_dir(self):
        return self.get_working_dir()

    def run_task(self, cmd, **kwargs):
        #if "grid" in kwargs: kwargs["grid"] = hyper_search_helper.load_hyper_search(kwargs["grid"])
        kwargs = {**env_helper.get_origin_job(), **kwargs}
        resp = apis_post(url_join(self.get_base_url(), "experiments"), data={"cmd": cmd, **kwargs})
        hyper_search = resp.get("hyper_search")
        if not hyper_search:
            error_msg = resp.get("error") or "Can't run experiment"
            raise CnvrgError(error_msg)
        return hyper_search

    def sync(self, get_output_by_regex=".*", **options):
        command = "cnvrg sync {args}".format(args=args_helper.args_to_string(options))
        return spawn_helper.run_sync(command, print_output=True, get_output_by_regex=get_output_by_regex)
