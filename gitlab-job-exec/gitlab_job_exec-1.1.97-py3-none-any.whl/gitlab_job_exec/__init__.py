# Standard library imports
import concurrent.futures
import copy
import itertools
import os
import string
import sys
import tempfile
import time
import typing

# Related third party imports
import dpath.util
import docker
import requests
import requests_file
import yaml


# Utils functions
def ensure_unix_path(path, full_path=True):
    if full_path and not path.startswith("/"):
        path = "/" + path
    return path.replace(":", "").replace("\\", "/")


# Global constant
COMPONENT_DIR = ensure_unix_path(os.getcwd())
COMPONENT_NAME = os.path.basename(COMPONENT_DIR)
DEFAULT_INCLUDE_PATTERN = "https://{group}.gitlab.io/{project}"
GITLAB_VARIABLES = {'CI_PIPELINE_ID': time.strftime("%Y%m%d%H%M", time.localtime()),
                    'CI_PIPELINE_IID': time.strftime("%Y%m%d%H%M", time.localtime()),
                    'CI_PIPELINE_SOURCE': "local",
                    'CI_PROJECT_DIR': COMPONENT_DIR,
                    'CI_PROJECT_NAME': COMPONENT_NAME,
                    'CI_PROJECT_NAMESPACE': os.path.basename(os.path.dirname(COMPONENT_DIR)),
                    'CI_PROJECT_PATH': "local/" + COMPONENT_NAME,
                    'CI_PROJECT_ROOT_NAMESPACE': "",
                    'CI_PROJECT_URL': "http://localhost/" + COMPONENT_NAME,
                    'CI_REGISTRY': "registry.gitlab.com",
                    'CI_REGISTRY_IMAGE': "registry.gitlab.com/local/" + COMPONENT_NAME,
                    'CI_SERVER_URL': "https://gitlab.com",
                    }
INVALID_JOB_NAMES = ["after_script",
                     "before_script",
                     "cache",
                     "default",
                     "image",
                     "include",
                     "services",
                     "stages",
                     "types",
                     "variables",
                     "workflow",
                     ]
TEMPLATE_URL = "https://gitlab.com/gitlab-org/gitlab/-/raw/master/lib/gitlab/ci/templates/"

# Global variables
__version__ = "1.1"

# Force output to utf-8
sys.stdout.reconfigure(encoding="utf-8")


class GitlabCI:
    # pylint: disable=too-few-public-methods

    def __init__(self,
                 filename: str,
                 include_pattern: typing.Optional[str] = DEFAULT_INCLUDE_PATTERN,
                 template_url: typing.Optional[str] = TEMPLATE_URL,
                 ):
        self.jobs = {}
        self.include_pattern = include_pattern.replace("{", "${")
        self.template_url = template_url + ("/" if not template_url.endswith("/") else "")

        with open(filename, "r") as gitlab_ci_file:
            gitlab_ci = yaml.load(gitlab_ci_file, Loader=yaml.SafeLoader)

        # Expand the includes
        with concurrent.futures.ThreadPoolExecutor() as executor:
            while 'include' in gitlab_ci and gitlab_ci['include']:
                includes = executor.map(self._get_include, gitlab_ci['include'])

                del gitlab_ci['include']
                for include in includes:
                    dpath.util.merge(gitlab_ci, include)

        # Expand the extends
        # NOTE: Not supporting an array of extends
        for job_name in gitlab_ci:
            while 'extends' in gitlab_ci[job_name]:
                job_parameters = gitlab_ci[job_name]
                extended_job_name = job_parameters.pop('extends')
                extended_job = copy.deepcopy(gitlab_ci[extended_job_name])
                dpath.util.merge(extended_job, job_parameters, flags=dpath.util.MERGE_REPLACE)
                gitlab_ci[job_name] = extended_job

        # Keep the expanded result
        self._detail = gitlab_ci

        # Create the defaults
        self.defaults = gitlab_ci.get('default', {})

        # Create the stages
        self.stages = gitlab_ci.get('stages', ["build", "test", "deploy"])

        # Create the global variables
        self.variables = gitlab_ci.get('variables', {})

        # Create the jobs
        for job_name, job_parameters in gitlab_ci.items():
            if job_name.startswith("."):
                continue
            if job_name in INVALID_JOB_NAMES:
                continue
            self.jobs[job_name] = GitlabJob(job_name,
                                            defaults=self.defaults,
                                            parameters=job_parameters,
                                            global_variables=self.variables,
                                            )

    def __str__(self):
        return yaml.dump(self._detail, default_flow_style=False)

    def _get_include(self,
                     detail: dict,
                     ) -> dict:

        # Define where to get to include file
        if 'file' in detail:
            if isinstance(detail['file'], list):
                # Return includes as a list of individual file include
                yaml_response = {'include': []}
                for file_to_include in detail['file']:
                    yaml_response['include'].append({'project': detail['project'], 'file': file_to_include})
                return yaml_response

            include_vars = {}
            include_vars['group'] = detail['project'].split("/")[0]
            include_vars['project'] = "/".join(detail['project'].split("/")[1:])

            detail['_included_from'] = string.Template(self.include_pattern).substitute(include_vars)
            url = detail['_included_from'] + detail['file']

        elif 'local' in detail:
            if detail.get('_included_from', ""):
                url = detail['_included_from'] + detail['local']
            else:
                url = "file://" + os.getcwd() + detail['local']

        elif 'remote' in detail:
            url = detail['remote']

        elif 'template' in detail:
            url = self.template_url + detail['template']

        else:
            raise RuntimeError("Unknown include type")

        # Get the include file
        request = requests.Session()
        request.mount('file://', requests_file.FileAdapter())
        response = request.get(url)
        response.raise_for_status()
        response.close()

        yaml_response = yaml.load(response.text, Loader=yaml.SafeLoader)
        if 'include' in yaml_response:
            for include in yaml_response['include']:
                include['_included_from'] = detail.get("_included_from", "")
        return yaml_response


class GitlabJob:
    # pylint: disable=too-few-public-methods
    # pylint: disable=too-many-instance-attributes

    def __init__(self,
                 name: str,
                 parameters: dict,
                 defaults: dict = None,
                 global_variables: dict = None,
                 ):
        defaults = defaults or {}
        global_variables = global_variables or {}

        # Keep the job parameters
        self._parameters = parameters

        # Populate data
        self.name = name
        self.stage = parameters.get('stage', "test")
        self.script = parameters.get('script', [])
        self.image = GitlabJob._unravel_parameter("image",
                                                  local_data=parameters,
                                                  global_data=defaults,
                                                  inherited=parameters.get('inherit', {}).get('default', True),
                                                  default="ruby:latest",
                                                  )
        self.before_script = GitlabJob._unravel_parameter("before_script",
                                                          local_data=parameters,
                                                          global_data=defaults,
                                                          inherited=parameters.get('inherit', {}).get('default', True),
                                                          default=[],
                                                          )
        self.services = GitlabJob._unravel_parameter("services",
                                                     local_data=parameters,
                                                     global_data=defaults,
                                                     inherited=parameters.get('inherit', {}).get('default', True),
                                                     default=[],
                                                     )

        # Populate variables
        self.variables = {}
        for var_name in itertools.chain(parameters.get('variables', []), global_variables):
            self.variables[var_name] = self._unravel_parameter(var_name,
                                                               local_data=parameters.get('variables', {}),
                                                               global_data=global_variables,
                                                               inherited=parameters.get('inherit', {}).get('variables',
                                                                                                           True,
                                                                                                           ),
                                                               default=None,
                                                               )
        self.variables = {k:v for (k, v) in self.variables.items() if v is not None}

    def __str__(self):
        return yaml.dump({self.name: self._parameters}, default_flow_style=False, indent=2)

    @staticmethod
    def _unravel_parameter(name: str,
                           local_data: dict,
                           global_data: dict,
                           inherited: typing.Union[list, bool],
                           default: typing.Any = None,
                           ) -> typing.Any:
        # Retrieve the proper value for the parameter
        # pylint: disable=no-else-return
        if name in local_data:
            return local_data[name]
        elif name not in global_data:
            return default
        elif isinstance(inherited, bool) and inherited:
            return global_data[name]
        elif isinstance(inherited, list) and name in inherited:
            return global_data[name]
        else:
            return default

    def _start_services(self,
                        pull_image: bool = True,
                        ) -> dict:
        # Local variables
        links = {}

        # Connect to docker
        docker_server = docker.from_env()

        # Process each service
        for service in self.services:
            if isinstance(service, str):
                image_name = service
                container_name = service.split(":")[0]
            else:
                image_name = service['name']
                container_name = service['alias']

            links[container_name] = None

            # Delete the container
            if docker_server.containers.list(all=True, filters={'name': container_name}):
                print("Stopping previously running service... ", end="", flush=True)
                docker_server.containers.get(container_name).remove(force=True)
                print("Done")

            # Pull image
            if pull_image:
                print("Pulling service image... ", end="", flush=True)
                docker_server.images.pull(image_name)
                print("Done")

            # Start the container
            print("Starting service {}... ".format(container_name), end="", flush=True)
            docker_server.containers.run(image_name,
                                         detach=True,
                                         name=container_name,
                                         privileged=bool(image_name == "docker:dind"),
                                         remove=True,
                                         )
            print("Done")

        return links

    def run(self,
            extra_variables: dict = None,
            extra_volumes: dict = None,
            pull_image: bool = True,
            user: str = "",
            ) -> int:
        # pylint: disable=too-many-locals

        extra_variables = extra_variables or {}
        extra_volumes = extra_volumes or {}

        # Connect to docker
        docker_server = docker.from_env()

        # Set the variables
        variables = copy.deepcopy(GITLAB_VARIABLES)
        dpath.util.merge(variables, self.variables)
        dpath.util.merge(variables, extra_variables)
        for name, value in variables.items():
            if not isinstance(value, str):
                variables[name] = str(value)
        if variables['CI_PROJECT_ROOT_NAMESPACE']:
            variables['CI_PROJECT_NAMESPACE'] = ensure_unix_path(os.path.join(variables['CI_PROJECT_ROOT_NAMESPACE'],
                                                                              variables['CI_PROJECT_NAMESPACE'],
                                                                              ),
                                                                 full_path=False,
                                                                 )
        else:
            variables['CI_PROJECT_ROOT_NAMESPACE'] = variables['CI_PROJECT_NAMESPACE']
        for name, value in variables.items():
            variables[name] = string.Template(value).substitute(variables)

        # Start services
        links = self._start_services(pull_image=pull_image)

        # Pull the image
        if isinstance(self.image, dict):
            docker_image = string.Template(self.image['name']).substitute(variables)
        else:
            docker_image = string.Template(self.image).substitute(variables)
        if pull_image:
            print("Pulling image... ", end="", flush=True)
            docker_server.images.pull(docker_image)
            print("Done")

        # Set the entrypoint
        entrypoint = None
        if isinstance(self.image, dict) and 'entrypoint' in self.image:
            entrypoint = self.image['entrypoint']

        # Create the script
        script = tempfile.NamedTemporaryFile(mode='w', prefix="job_", suffix=".sh", newline="\n")
        for command in self.before_script + self.script:
            script.write(command + "\n")
        script.flush()

        # Set volumes to mount
        docker_dir = ensure_unix_path(os.path.expanduser("~/.docker"))
        project_dir = variables['CI_PROJECT_DIR']
        volumes = {ensure_unix_path(script.name): {'bind': "/tmp/job.sh", 'mode': 'ro'},
                   docker_dir: {'bind': "/root/.docker", 'mode': 'ro'},
                   project_dir: {'bind': project_dir, 'mode': 'rw'},
                   '/var/run/docker.sock': {'bind': "/var/run/docker.sock",
                                            'mode': 'rw',
                                            },
                   }
        dpath.util.merge(volumes, extra_volumes)

        # Set the command
        # NOTE: Emulating GitLab's step_script (https://gitlab.com/gitlab-org/gitlab-runner/-/blob/79911f89b70dcbb1f16ca7a1242d5919aef52c4a/shells/bash.go#L17)     # pylint: disable=line-too-long
        command = "sh -c \""
        command += "if   [ -x /usr/local/bin/bash ]; then detected_shell=/usr/local/bin/bash;"    \
                   "elif [ -x /usr/bin/bash       ]; then detected_shell=/usr/bin/bash      ;"    \
                   "elif [ -x /bin/bash           ]; then detected_shell=/bin/bash          ;"    \
                   "elif [ -x /usr/local/bin/sh   ]; then detected_shell=/usr/local/bin/sh  ;"    \
                   "elif [ -x /usr/bin/sh         ]; then detected_shell=/usr/bin/sh        ;"    \
                   "elif [ -x /bin/sh             ]; then detected_shell=/bin/sh            ;"    \
                   "elif [ -x /busybox/sh         ]; then detected_shell=/busybox/sh        ;"    \
                   "else echo 'shell not found' >$2; exit 1                                 ;"    \
                   "fi                                                                      ;"    \
                   "exec ${detected_shell} -ex -o pipefail /tmp/job.sh                      ;"
        command += "\""

        # Start the container
        container = docker_server.containers.run(docker_image,
                                                 command=command,
                                                 detach=True,
                                                 entrypoint=entrypoint,
                                                 environment=variables,
                                                 links=links,
                                                 user=user,
                                                 volumes=volumes,
                                                 working_dir=variables['CI_PROJECT_DIR'],
                                                 )
        for line in container.logs(stream=True):
            print(line.decode("utf-8"), end="", flush=True)

        result = container.wait()['StatusCode']
        container.remove()

        # Stop services
        for container_name in links:
            docker_server.containers.get(container_name).stop()

        return result
