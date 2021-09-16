# -*- coding: utf-8 -*-
#
# (C) Copyright 2020 Karellen, Inc. (https://www.karellen.co/)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import textwrap

from pybuilder.core import use_plugin, init, before, depends, task

use_plugin("python.core")
use_plugin("copy_resources")
use_plugin("python.unittest")
use_plugin("python.integrationtest")
use_plugin("python.flake8")
use_plugin("python.distutils")
use_plugin("python.pycharm")
use_plugin("python.cram")
use_plugin("python.sphinx")
use_plugin("pypi:pybuilder_header_plugin")


@init
def configure(project):
    project.build_depends_on("sphinx_rtd_theme", ">=0.0.1")

    # Unit test Coverage Configuration
    project.set_property("coverage_threshold_warn", 100)
    project.set_property("coverage_branch_threshold_warn", 100)
    project.set_property("coverage_branch_partial_threshold_warn", 100)
    project.set_property("coverage_break_build", True)
    project.set_property("coverage_exceptions", [])

    # Flake8 Configuration
    project.set_property("flake8_break_build", True)
    project.set_property("flake8_extend_ignore", "E303")
    project.set_property("flake8_include_test_sources", True)
    project.set_property("flake8_include_scripts", True)
    project.set_property("flake8_max_line_length", 130)

    # Copyright Header
    project.set_property("pybuilder_header_plugin_break_build", True)
    project.set_property("pybuilder_header_plugin_expected_header",
                         textwrap.dedent("""\
                         # -*- coding: utf-8 -*-
                         #
                         # (C) Copyright 2020 Karellen, Inc. (https://www.karellen.co/)
                         #
                         # Licensed under the Apache License, Version 2.0 (the "License");
                         # you may not use this file except in compliance with the License.
                         # You may obtain a copy of the License at
                         #
                         #     http://www.apache.org/licenses/LICENSE-2.0
                         #
                         # Unless required by applicable law or agreed to in writing, software
                         # distributed under the License is distributed on an "AS IS" BASIS,
                         # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
                         # See the License for the specific language governing permissions and
                         # limitations under the License.
                         #
                         """))
    project.set_property("pybuilder_header_plugin_exclude_patterns", [])

    # Cram Configuration
    project.set_property("cram_fail_if_no_tests", True)

    # Distutils
    project.set_property("distutils_classifiers", ["Development Status :: 5 - Production/Stable",
                                                   "Environment :: Console",
                                                   "Intended Audience :: Developers",
                                                   "License :: OSI Approved :: Apache Software License",
                                                   "Programming Language :: Python",
                                                   ]
                         )
    project.set_property("distutils_commands", ["sdist", "bdist_wheel"])
    project.set_property("distutils_upload_skip_existing", True)
    project.set_property("distutils_upload_sign", True)
    project.set_property("distutils_upload_sign_identity", "5F4AFAA3")
    project.set_property("distutils_upload_repository_key", "pypi-karellen")
    project.set_property("distutils_readme_description", True)
    project.set_property("distutils_description_overwrite", True)
    project.set_property("distutils_readme_file", "README.md")

    # Sphinx
    project.set_property("sphinx_output_per_builder", True)
    project.set_property("sphinx_run_apidoc", True)
    project.set_property("sphinx_apidoc_extra_args", ["-l", "-e"])
    project.set_property("sphinx_build_extra_args", ["-E"])


@before("sphinx_generate_documentation")
def set_sphinx_html_path(project):
    import sphinx_rtd_theme

    sphinx_conf = project.get_property("sphinx_project_conf")
    sphinx_conf["html_theme"] = "sphinx_rtd_theme"
    sphinx_conf["html_theme_path"] = [sphinx_rtd_theme.get_html_theme_path()]

    # Napoleon settings
    sphinx_conf["extensions"].append("sphinx.ext.napoleon")
    sphinx_conf["napoleon_google_docstring"] = True
    sphinx_conf["napoleon_numpy_docstring"] = False
    sphinx_conf["napoleon_include_init_with_doc"] = False
    sphinx_conf["napoleon_include_private_with_doc"] = False
    sphinx_conf["napoleon_include_special_with_doc"] = False
    sphinx_conf["napoleon_use_admonition_for_examples"] = False
    sphinx_conf["napoleon_use_admonition_for_notes"] = False
    sphinx_conf["napoleon_use_admonition_for_references"] = False
    sphinx_conf["napoleon_use_ivar"] = False
    sphinx_conf["napoleon_use_param"] = True
    sphinx_conf["napoleon_use_rtype"] = True
    sphinx_conf["napoleon_use_keyword"] = True


@task
@depends("check_source_file_headers")
def verify(project, logger, reactor):
    pass
