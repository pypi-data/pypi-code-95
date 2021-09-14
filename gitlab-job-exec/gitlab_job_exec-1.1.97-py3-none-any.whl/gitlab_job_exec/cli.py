#! /usr/bin/env python3

# Standard library imports
import os
import sys

# Related third party imports
import pkg_resources
import configargparse

# Local application/library specific imports
import gitlab_job_exec


# Class taken from the argparse standard library for python3.9
# This class will no longer be needed when the minimal python version is >= 3.9
class BooleanOptionalAction(configargparse.Action):
    # pylint: disable=redefined-builtin,too-many-arguments
    def __init__(self,
                 option_strings,
                 dest,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None):

        _option_strings = []
        for option_string in option_strings:
            _option_strings.append(option_string)

            if option_string.startswith('--'):
                option_string = '--no-' + option_string[2:]
                _option_strings.append(option_string)

        # Commented since we already use the ArgumentDefaultsHelpFormatter class to show defaults
        # if help is not None and default is not None:
        #     help += f" (default: {default})"

        super().__init__(
            option_strings=_option_strings,
            dest=dest,
            nargs=0,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        if option_string in self.option_strings:
            setattr(namespace, self.dest, not option_string.startswith('--no-'))

    def format_usage(self):
        return ' | '.join(self.option_strings)


def get_version():
    version = gitlab_job_exec.__version__

    distribution = pkg_resources.AvailableDistributions()['gitlab-job-exec']
    if distribution:
        version = distribution[0].version

    return "%(prog)s " + version


def parse_options(argv: list,
                  ) -> configargparse.Namespace:
    parser = configargparse.ArgumentParser(formatter_class=configargparse.ArgumentDefaultsHelpFormatter,
                                           default_config_files=['~/.gitlab-job-exec.cfg'],
                                           )
    parser.add_argument("-c", "--config-file",
                        is_config_file=True,
                        help="Config file path. Used in addition to the default one",
                        )
    parser.add_argument("--list", action='store_true', help="list available jobs")
    parser.add_argument("--describe", action='store_true', help="show details of given jobs")
    parser.add_argument("--pull", action=BooleanOptionalAction, default=True,
                        help="pull (or don't pull) the docker image before running",
                        )
    parser.add_argument("--root", action='store_true', help="run as root in the container")
    parser.add_argument("--file", default=".gitlab-ci.yml", help="path to .gitlab-ci.yml file to use")
    parser.add_argument("-e", "--extra-vars",
                        action="append",
                        help="extra environment variables to pass to the jobs as key=value, "
                             "prepend with @ to pass filename containing the variables",
                        )
    parser.add_argument("--default-vars",
                        action="append",
                        help="same as --extra-vars, but with lower priority. "
                             "Can be used in configuration file for common extra vars",
                        )
    parser.add_argument("--extra-volumes",
                        action="append",
                        help="extra volumes to mount on the job's container. "
                             "Syntax is same as '-v' when doing 'docker run'. "
                             "To set the mode, add it after the container path (ex: '/x/y:/foo/bar:ro')",
                        )
    parser.add_argument("--include-pattern",
                        env_var="INCLUDE_PATTERN",
                        default=gitlab_job_exec.DEFAULT_INCLUDE_PATTERN,
                        help="URL pattern to use for the 'include' statement. "
                             "Available variables are 'group' and 'project'. "
                             "The values will correspond to the 'project' key of the include ({group}/{project}). "
                             "This will follow defaults GitLab Pages URL with subgroup being part of {project}. "
                             "Supported schemes are http://, https:// and file://",
                        )
    parser.add_argument("--template-url",
                        default=gitlab_job_exec.TEMPLATE_URL,
                        help="Base URL to use to fetch GitLab templates for 'template' includes."
                        )
    parser.add_argument("-V", "--version",
                        action='version',
                        version=get_version(),
                        )
    parser.add_argument("jobs", nargs="*")

    args = parser.parse_args(argv)

    # Parse extra environment variables
    extra_vars = {}
    for env_vars in ['default_vars', 'extra_vars']:
        if getattr(args, env_vars) is not None:
            for arg in getattr(args, env_vars):
                for variable in arg.split(" "):
                    if variable.startswith("@"):
                        with open(variable[1:], "r") as var_file:
                            for line in var_file.readlines():
                                line = line.strip()
                                extra_vars[line.split("=")[0]] = "=".join(line.split("=")[1:])
                    else:
                        extra_vars[variable.split("=")[0]] = "=".join(variable.split("=")[1:])

    args.extra_vars = extra_vars

    # Parse extra volumes to mount
    extra_volumes = {}
    if args.extra_volumes is not None:
        for volume in args.extra_volumes:
            name, bind, *mode = volume.split(":")
            mode = mode[0] if mode else "rw"

            extra_volumes[name] = {'bind': bind,
                                   'mode': mode,
                                   }
    args.extra_volumes = extra_volumes

    return args


def main():
    options = parse_options(sys.argv[1:])

    # Load the .gitlab-ci.yml file
    gitlab_ci = gitlab_job_exec.GitlabCI(options.file,
                                         include_pattern=options.include_pattern,
                                         template_url=options.template_url,
                                         )

    # Only list available jobs
    if options.list:
        for stage in gitlab_ci.stages:
            print("Stage: " + stage)
            for job_name, job in gitlab_ci.jobs.items():
                if job.stage == stage:
                    print("    " + job.name)
        sys.exit(0)

    # Print jobs details
    if options.describe:
        for job_name in options.jobs:
            print(gitlab_ci.jobs[job_name])
        sys.exit(0)

    # Execute each job in the order given
    for job_name in options.jobs:
        # Set the user
        if options.root:
            user = "0:0"
        else:
            user = str(os.getuid()) + ":" + str(os.getgid())

        # Run the job
        result = gitlab_ci.jobs[job_name].run(user=user,
                                              pull_image=options.pull,
                                              extra_variables=options.extra_vars,
                                              extra_volumes=options.extra_volumes,
                                              )

        # Stop in case of error
        if result:
            sys.exit(result)


if __name__ == "__main__":
    main()
