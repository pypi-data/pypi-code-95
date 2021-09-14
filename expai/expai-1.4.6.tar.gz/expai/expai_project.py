import requests
import logging
from expai.expai_explainer import ExpaiModelExplainer
from expai.expai_performance import ExpaiModelPerformance
from expai.utils import generate_response
from expai.expai_explanation import ExpaiExplanation
import io
import pandas as pd
import ast


class ExpaiProject:
    def __init__(self, project_id: str, access_token: str, headers: dict, server_name: str, session):

        self.project_id = project_id

        self.server_name = server_name
        self.access_token = access_token

        self.headers = headers
        
        self.sess = session

    #########################
    ###      MODELS       ###
    #########################

    def model_list(self, search_by: str = None, exact_search: str = None):
        """
        List all models within the project
        :return: list of models
        """

        if exact_search is not None:
            response = self.sess.request("GET",
                                         self.server_name + "/api/projects/{}/model/list/contains/{}".format(
                                             self.project_id, exact_search),
                                         headers=self.headers)

            if 'models' in response.json().keys():
                for model in response.json()['models']:
                    if model['model_name_des'] == exact_search:
                        return model
            logging.error(
                "We could not find a model with this exact name. Try again or consider using search_by parameter to find similar samples")
            return None

        elif search_by is not None:
            response = self.sess.request("GET",
                                         self.server_name + "/api/projects/{}/model/list/contains/{}".format(
                                             self.project_id, search_by),
                                         headers=self.headers)
            return generate_response(response, ['models'])

        else:
            response = self.sess.request("GET",
                                         self.server_name + "/api/projects/{}/model/list".format(self.project_id),
                                         headers=self.headers)

            return generate_response(response, ['models'])


    def create_model(self, model_path: str = None, model_name: str = None,
                     model_summary: str = None, model_library: str = None, model_objective: str = None,
                     model_prediction_type: str = None, output_classes: list = None, model_cutoff: float = None):
        """
        Create a new model for a project.
        :param model_path: path where your model is stored locally
        :param is_supervised: Indicate whether the model is supervised
        :param model_name: Name you want to give to the model
        :return: True if successful
        """
        assert model_name is not None, "To create a model you must give it a model_name"
        assert model_path is not None, "To create a model you must specify the path to the stored model"
        assert model_library is not None, "Please, indicate the model_library. Refer to documentation for further information"
        assert model_objective is not None, "Please, indicate the model_objective. Refer to documentation for further information"
        assert model_prediction_type is not None, "Please, indicate the model_prediction_type. Refer to documentation for further information"

        if model_cutoff is not None:
            assert 0 < model_cutoff < 1, "Cutoff value must be between 0 and 1"

        data = {"model_name_des": model_name,
                "model_summary_des": model_summary,
                "is_supervised_flag": 1,
                "model_cutoff_num": model_cutoff,
                'model_library_des': model_library,
                'model_objective_des': model_objective,
                'model_prediction_type_des': model_prediction_type,
                'output_classes_des': ','.join(str(e) for e in output_classes) if output_classes is not None else None}

        files = {'model_file': open(model_path, 'rb')}
        headers = {'access_token': self.access_token}

        response = self.sess.request("POST", self.server_name + "/api/projects/{}/model/create".format(self.project_id),
                                    data=data, headers=headers, files=files)

        if response.ok:
            return "Model successfully created with id {}".format(response.json()['model_id'])
        else:
            return generate_response(response)

    def delete_model(self, model_name: str = None, model_id: str = None):
        """
        Delete a model within a project
        :param model_name: name of the model you want to remove
        :param model_id: Id for the model you want to remove (optional)
        :return: True if successful
        """
        assert model_id is not None or model_name is not None, "You must indicate the model_name or model_id"

        if model_id is None:
            model_id = self._get_model_id_from_name(model_name)

        response = self.sess.request("DELETE",
                                    self.server_name + "/api/projects/{}/model/{}".format(self.project_id, model_id),
                                    headers=self.headers)

        if response.ok:
            return "Model successfully deleted"
        else:
            return generate_response(response)

    def get_model_explainer(self, model_name: str = None, model_id: str = None):
        """
        Get a Python object that will enable you to interact with a project and its models.
        :param model_name: Name of the project
        :param model_id: Id of the project (optional)
        :return: ExpaiModel object
        """
        assert model_name is not None or model_id is not None, "You must provide a project name or project id"

        if model_id is None:
            model_id = self._get_model_id_from_name(model_name)

        if model_id is not None:
            return ExpaiModelExplainer(model_id, self.project_id, self.access_token, self.headers, self.server_name, self.sess, self)
        else:
            logging.error("We could not find your model. Please, check your name or try using model_id as parameter")

    def get_model_performance(self, model_name: str = None, model_id: str = None):
        """
        Get a Python object that will enable you to interact with a project and its models.
        :param model_name: Name of the project
        :param model_id: Id of the project (optional)
        :return: ExpaiModel object
        """
        assert model_name is not None or model_id is not None, "You must provide a project name or project id"

        if model_id is None:
            model_id = self._get_model_id_from_name(model_name)

        if model_id is not None:
            return ExpaiModelPerformance(model_id, self.project_id, self.access_token, self.headers, self.server_name, self.sess, self)
        else:
            logging.error("We could not find your model. Please, check your name or try using model_id as parameter")

    def update_model(self, model_name: str = None, model_id: str = None, update_info: dict = None):
        """
        Update a sample withing a project

        :param sample_name:
        :param sample_id:
        :param update_info: information to be updated in a dictionary
        :return:
        """
        assert model_id is not None or model_name is not None, "You must indicate the model_name or model_id"
        assert update_info is not None, "You must provide the update_info dictionary with the values to be updated"

        if model_id is None:
            model_id = self._get_model_id_from_name(model_name)

            if model_id is None:
                logging.error(
                    "We could not find any model matching that name. Please, try again or use model_id as parameter")
                return False

        response = self.sess.request("PATCH",
                                    self.server_name + "/api/projects/{}/model/{}".format(self.project_id, model_id),
                                    headers=self.headers, json=update_info)

        if response.ok:
            return "Model with id {} successfully updated".format(model_id)
        else:
            return generate_response(response)

    def _get_model_id_from_name(self, model_name: str = None):

        model_list = self.model_list()
        model_list = model_list.get('models')

        if model_list is None:
            raise Exception('Model not found')

        for model in model_list:
            if model['model_name_des'] == model_name:
                return model['model_id']
        return None

    #########################
    ###      SAMPLES      ###
    #########################

    def sample_list(self, search_by: str = None, exact_search: str = None):
        """
        List all samples associated with this project
        :return: list of samples
        """

        if exact_search is not None:
            response = self.sess.request("GET",
                                         self.server_name + "/api/projects/{}/sample/list/contains/{}".format(self.project_id, exact_search),
                                         headers=self.headers)

            if 'samples' in response.json().keys():
                for sample in response.json()['samples']:
                    if sample['sample_name_des'] == exact_search:
                        return sample
            logging.error("We could not find a sample with this exact name. Try again or consider using search_by parameter to find similar samples")
            return None

        elif search_by is not None:
            response = self.sess.request("GET",
                                         self.server_name + "/api/projects/{}/sample/list/contains/{}".format(
                                             self.project_id, search_by),
                                         headers=self.headers)
            return generate_response(response, ['samples'])

        else:
            response = self.sess.request("GET", self.server_name + "/api/projects/{}/sample/list".format(self.project_id),
                                    headers=self.headers)

            return generate_response(response, ['samples'])

    def create_sample(self, sample_path: str = None, sample_name: str = None, sample_separator: str = None, sample_target_col: str = None,
                      sample_encoding: str = 'utf-8', is_display = False, reference_sample_id: str = None, reference_sample_name: str = None,
                      display_sample_id: str = None, display_sample_name: str = None, sample_summary: str = None, protected_columns: list = None,
                      drop_columns: list = None):
        """
        Create a new sample for the project
        :param sample_target_col: target column for the model
        :param sample_path: local path to the stored file
        :param sample_name: name for your new file
        :param sample_separator: separator for the sample columns
        :param sample_encoding: encoding of the file (optional). Default: utf-8.
        :return: True if successful
        """
        assert sample_name is not None, "To create a sample you must give it a sample_name"
        assert sample_path is not None, "To create a sample you must specify the path to the stored file"
        assert sample_separator is not None, "Please, specify the file separator"

        if is_display is True:
            assert reference_sample_id is not None or reference_sample_name is not None, "Please, specify the original sample id or name for this display"

            if reference_sample_id is None:
                reference_sample_id = self._get_sample_id_from_name(reference_sample_name)
                if reference_sample_id is None:
                    logging.error(
                        "We could not find any sample matching that name. Please, try again or use reference_sample_id as parameter")
                    return False
        else:
            if display_sample_name is not None:
                display_sample_id = self._get_sample_id_from_name(display_sample_name)

        data = {"sample_name_des": sample_name,
                "sample_file_separator_des": sample_separator,
                "sample_file_encoding_des": sample_encoding,
                "sample_target_col": sample_target_col,
                "is_display": 1 if is_display is True else 0,
                "original_sample_id": reference_sample_id,
                "display_sample_id": display_sample_id,
                'sample_summary_des': sample_summary,
                'sample_protected_columns_des': ','.join(protected_columns) if protected_columns else None,
                'sample_drop_columns_des': ','.join(drop_columns) if drop_columns else None}

        files = {'sample_file': open(sample_path, 'r', encoding=sample_encoding)}

        headers = {'access_token': self.access_token}

        response = self.sess.request("POST", self.server_name + "/api/projects/{}/sample/create".format(self.project_id),
                                    data=data, headers=headers, files=files)

        if response.ok:
            return "Sample successfully created with id {}".format(response.json()['sample_id'])
        else:
            return generate_response(response)

    def delete_sample(self, sample_name: str = None, sample_id: str = None):
        """
        Delete a model within a project
        :param model_name: name of the model you want to remove
        :param model_id: Id for the model you want to remove (optional)
        :return: True if successful
        """
        assert sample_id is not None or sample_name is not None, "You must indicate the sample_name or sample_id"

        if sample_id is None:
            sample_id = self._get_sample_id_from_name(sample_name)

            if sample_id is None:
                logging.error(
                    "We could not find any sample matching that name. Please, try again or use sample_id as parameter")
                return False

        response = self.sess.request("DELETE",
                                    self.server_name + "/api/projects/{}/sample/{}".format(self.project_id, sample_id),
                                    headers=self.headers)

        if response.ok:
            return "Sample successfully deleted"
        else:
            return generate_response(response)

    def update_sample(self, sample_name: str = None, sample_id: str = None, update_info: dict = None):
        """
        Update a sample withing a project

        :param sample_name:
        :param sample_id:
        :param update_info: information to be updated in a dictionary
        :return:
        """
        assert sample_id is not None or sample_name is not None, "You must indicate the sample_name or sample_id"
        assert update_info is not None, "You must provide the update_info dictionary with the values to be updated"

        if sample_id is None:
            sample_id = self._get_sample_id_from_name(sample_name)

            if sample_id is None:
                logging.error(
                    "We could not find any sample matching that name. Please, try again or use sample_id as parameter")
                return False

        response = self.sess.request("PATCH",
                                    self.server_name + "/api/projects/{}/sample/{}".format(self.project_id, sample_id),
                                    headers=self.headers, json=update_info)

        if response.ok:
            return "Sample with id {} successfully updated".format(sample_id)
        else:
            return generate_response(response)

    def append_sample(self, sample_name: str = None, sample_id: str = None, sample_path: str = None, sample_encoding: str = 'utf-8'):
        assert sample_id is not None or sample_name is not None, "You must indicate the sample_name or sample_id"
        assert sample_path is not None, "Please, provide the local path for the sample you want to update"

        if sample_id is None:
            sample_id = self._get_sample_id_from_name(sample_name)

            if sample_id is None:
                logging.error(
                    "We could not find any sample matching that name. Please, try again or use sample_id as parameter")
                return False

        files = {'sample_file': open(sample_path, 'r', encoding=sample_encoding)}

        headers = {'access_token': self.access_token}

        response = self.sess.request("POST", self.server_name + "/api/projects/{}/sample/{}/append".format(self.project_id, sample_id),
                                     headers=headers, files=files)

        if response.ok:
            return "Successfully appended to sample with id {}".format(sample_id)
        else:
            return generate_response(response)

    def get_sample(self, sample_name: str = None, sample_id: str = None, subset_filters: dict = None, drop_target: bool = None, drop_columns: bool = None):
        """
        Returns a pandas DataFrame from your stored sample.
        :param sample_name: Name of the sample (use this parameter OR sample_id)
        :param sample_id: Unique ID for the sample
        :param subset_filters: Dictionary with filters (see documentation)
        :param drop_target: True if you want to drop the target column
        :param drop_columns: True if you want to drop your drop columns
        :return: dataframe
        """
        assert sample_id is not None or sample_name is not None, "You must indicate the sample_name or sample_id"

        if sample_id is None:
            sample_id = self._get_sample_id_from_name(sample_name)

            if sample_id is None:
                logging.error(
                    "We could not find any sample matching that name. Please, try again or use sample_id as parameter")
                return False

        data = {"subset_filters": subset_filters,
                "drop_target_cols": drop_target,
                "drop_cols": drop_columns}

        response = self.sess.request("POST", self.server_name + "/api/projects/{}/sample/{}/get".format(self.project_id, sample_id),
                                     headers=self.headers, json=data)

        if response.ok:
            if 'data' in response.json():
                df = pd.DataFrame(response.json().get('data'))
                df = df.rename(columns={'__expai_index__': 'index'})
                df['index'] = df['index'].astype(int)
                df = df.set_index('index')
                return df.sort_index()
            else:
                raise Exception("There was en error generating the DataFrame. No data was returned from API. Please, try again.")
        else:
            return generate_response(response)


    def _get_sample_id_from_name(self, sample_name: str = None):
        sample_list = self.sample_list()
        sample_list = sample_list.get('samples')

        if sample_list is None:
            return None

        for sample in sample_list:
            if sample['sample_name_des'] == sample_name:
                return sample['sample_id']
        return None

    #########################
    ###    EXPLANATIONS   ###
    #########################

    def explanation_list(self, search_by: str = None, exact_search: str = None):
        """
        List all samples associated with this project
        :return: list of samples
        """

        if exact_search is not None:
            response = self.sess.request("GET",
                                         self.server_name + "/api/projects/{}/explanation/list/contains/{}".format(self.project_id, exact_search),
                                         headers=self.headers)

            if 'explanations' in response.json().keys():
                for exp in response.json()['explanations']:
                    if exp['explanation_name_des'] == exact_search:
                        return ExpaiExplanation(model_id=exp['model_id'],
                                                project_id=exp['project_id'],
                                                sample_id=exp['sample_id'],
                                                access_token=self.access_token,
                                                server_name=self.server_name,
                                                headers=self.headers,
                                                session=self.sess,
                                                project=self)
            logging.error("We could not find an explanation with this exact name. Try again or consider using search_by parameter to find similar explanations")
            return None

        elif search_by is not None:
            response = self.sess.request("GET",
                                         self.server_name + "/api/projects/{}/explanation/list/contains/{}".format(
                                             self.project_id, search_by),
                                         headers=self.headers)
            return generate_response(response, ['explanations'])

        else:
            response = self.sess.request("GET", self.server_name + "/api/projects/{}/explanation/list".format(self.project_id),
                                         headers=self.headers)

            return generate_response(response, ['explanations'])