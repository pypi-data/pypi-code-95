from test.conftest import USE_MOCK
from test.util import random_string

import pytest
from mock import Mock, patch

import savvihub
from savvihub.util.constant import PROJECT_TYPE_CLI_DRIVEN
from savvihub.util.exception import InvalidProjectError


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestProject:
    project_name = random_string()

    @pytest.mark.order(index=1)
    def test_create_project(self):
        savvihub.create_project(PROJECT_TYPE_CLI_DRIVEN, self.project_name)

    def test_read_project(self):
        savvihub.read_project(self.project_name)

    def test_list_projects(self):
        savvihub.list_projects()

    def test_clone_project(self):
        # Only applies to version-control project
        pass


def test_get_project_name():
    with patch.object(savvihub.vessl_api, "project", None):
        with pytest.raises(InvalidProjectError):
            savvihub.project._get_project_name()

    project_name = "proj"
    assert savvihub.project._get_project_name(project_name=project_name) == project_name

    project = Mock()
    project.name = project_name
    with patch.object(savvihub.vessl_api, "project", project):
        assert savvihub.project._get_project_name() == project_name


def test_get_project():
    with patch.object(savvihub.vessl_api, "project", None):
        with pytest.raises(InvalidProjectError):
            savvihub.project._get_project()

    project_name = "proj"

    project = Mock()
    project.name = project_name
    with patch.object(savvihub.project, "read_project", return_value=project):
        assert (
            savvihub.project._get_project(project_name=project_name).name
            == project_name
        )

    with patch.object(savvihub.vessl_api, "project", project):
        assert savvihub.project._get_project().name == project_name
