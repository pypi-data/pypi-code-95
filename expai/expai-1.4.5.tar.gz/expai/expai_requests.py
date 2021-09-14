import requests
import logging
from expai.expai_project import ExpaiProject
from expai.utils import generate_response


class ExpaiAccount:
    def __init__(self, email: str = None, user_pass: str = None, access_token: str = None, server_name: str = "https://api.expai.io:443"):
        assert email is not None and user_pass is not None or access_token is not None, "Please, introduce your email and password or access_token"

        self.server_name = server_name
        self.email = email

        if access_token is None:
            self.headers = {
                'Content-Type': 'application/json'
            }

            json = {
                "email_des": email,
                "password_des": user_pass
            }

            self.sess = requests.session()
            response = self.sess.post(self.server_name + "/api/auth/login", headers=self.headers, json=json)

            if not response.ok:
                logging.error("Invalid credentials, please check them and try again. Thank you.")

            self.access_token = response.json().get('access_token')
            self.headers['access_token'] = self.access_token

        else:
            self.access_token = access_token

            self.headers = {
                'Content-Type': 'application/json',
                'access_token': access_token
            }

            self.sess = requests.session()
            response = self.sess.get(self.server_name + "/api/auth/check", headers=self.headers)
            if not response.ok:
                raise Exception("Please, introduce a valid token.")

    def project_list(self, search_by: str = None, exact_search: str = None):
        """
        Returns the list of projects for the user
        :return: list of projects
        """

        if exact_search is not None:
            response = self.sess.request("GET",
                                         self.server_name + "/api/projects/list/contains/{}".format(exact_search),
                                         headers=self.headers)

            if 'projects' in response.json().keys():
                for project in response.json()['projects']:
                    if project['project_name_des'] == exact_search:
                        return project
            logging.error(
                "We could not find a sample with this exact name. Try again or consider using search_by parameter to find similar samples")
            return None

        elif search_by is not None:
            response = self.sess.request("GET",
                                         self.server_name + "/api/projects/list/contains/{}".format(search_by),
                                         headers=self.headers)
            return generate_response(response, ['projects'])

        else:
            response = self.sess.request("GET", self.server_name + "/api/projects/list", headers=self.headers)

            return generate_response(response, ['projects'])


    def create_project(self, project_name: str = None, project_description: str = None):
        """
        Create a new project
        :param project_id: Name for the project
        :param project_description: Description for the project
        :return: True if successful
        """
        assert project_name is not None, "Please, introduce a project_id"

        payload = {"project_name_des": project_name,
                   'project_description_des': project_description}

        response = self.sess.request("POST", self.server_name + "/api/projects/create", headers=self.headers,
                                     json=payload)

        if response.ok:
            return "Project successfully created with id: {}".format(response.json()['project_id'])
        else:
            return generate_response(response)

    def delete_project(self, project_name: str = None, project_id: str = None):
        """
        Delete a project. You must indicate project_id or project_name
        :param project_id: id for the project (optional).
        :param project_name: name of the project.
        :return:
        """
        assert project_id is not None or project_name is not None, "To delete a project you must specify its project_id or project_name"

        if project_id is None:
            project_id = self._get_project_id_from_name(project_name)

        response = self.sess.request("DELETE", self.server_name + "/api/projects/{}".format(project_id),
                                     headers=self.headers)

        if response.ok:
            return "Project successfully deleted"
        else:
            return generate_response(response)

    def get_project(self, project_name: str = None, project_id: str = None):
        """
        Get a Python object that will enable you to interact with a project and its models.
        :param project_name: Name of the project
        :param project_id: Id of the project (optional)
        :return: ExpaiProject object
        """
        assert project_name is not None or project_id is not None, "You must provide a project name or project id"

        if project_id is None:
            project_id = self._get_project_id_from_name(project_name)

        if project_id is not None:
            return ExpaiProject(project_id, self.access_token, self.headers, self.server_name, self.sess)
        else:
            logging.error("We could not find your project. Please, check your name or try using project_id as parameter")
            return None

    def update_project(self, project_name: str = None, project_id: str = None, update_info: dict = None):
        """
        Update a project
        """
        assert project_id is not None or project_name is not None, "You must indicate the project_name or project_id"
        assert update_info is not None, "You must provide the update_info dictionary with the values to be updated"

        if project_id is None:
            project_id = self._get_project_id_from_name(project_name)

            if project_id is None:
                logging.error(
                    "We could not find any sample matching that name. Please, try again or use sample_id as parameter")
                return False

        response = self.sess.request("PATCH",
                                    self.server_name + "/api/projects/{}".format(project_id),
                                    headers=self.headers, json=update_info)

        if response.ok:
            return "Project with id {} successfully updated".format(project_id)
        else:
            return generate_response(response)

    def _get_project_id_from_name(self, project_name: str = None):
        project = self.project_list(exact_search=project_name)
        if project is not None:
            return project['project_id']

        return None

    def get_allowed_models(self):
        """
        Get a Python object that will enable you to interact with a project and its models.
        """
        response = self.sess.request("GET",
                                     self.server_name + "/api/models/get_allowed",
                                     headers=self.headers)

        return generate_response(response, ['models_category', 'models_objective', 'models_prediction', 'models_library'])

    def get_allowed_files(self):
        """
        Get a Python object that will enable you to interact with a project and its models.
        """
        response = self.sess.request("GET",
                                     self.server_name + "/api/files/get_allowed",
                                     headers=self.headers)

        return generate_response(response, ["files_type"])
