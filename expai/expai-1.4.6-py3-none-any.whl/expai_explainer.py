import logging
from expai.utils import generate_response
import numpy as np
from expai.expai_explanation import ExpaiExplanation
from expai.constants import explanation_types


class ExpaiModelExplainer:
    def __init__(self, model_id: str, project_id: str, access_token: str, headers: dict, server_name: str, session, project):
        self.model_id = model_id
        self.project_id = project_id

        self.server_name = server_name
        self.access_token = access_token

        self.headers = headers

        self.sess = session
        self.project = project

    def _get_sample_id_from_name(self, sample_name: str = None):

        sample_list = self.project.sample_list()
        sample_list = sample_list.get('samples')

        if sample_list is None:
            raise Exception('Sample not found')

        for sample in sample_list:
            if sample['sample_name_des'] == sample_name:
                return sample['sample_id']
        return None

    def get_allowed_explanations(self):
        response = self.sess.request("GET", self.server_name + "/api/explain/get_allowed", headers=self.headers)

        return generate_response(response, ['explanations'])


    def explain_model(self, sample_name: str = None, sample_id: str = None, subset_indexes: list = None, target_class: str = None):
        assert sample_name is not None or sample_id is not None, "You must provide a sample name or id for the explanation"

        if sample_id is None:
            sample_id = self._get_sample_id_from_name(sample_name)

            if sample_id is None:
                logging.error(
                    "We could not find any sample matching that name. Please, try again or use sample_id as parameter")
                return None

        json = {
            "sample_id": sample_id,
            "subset_indexes": subset_indexes,
            "target_class": target_class
        }

        response = self.sess.post(self.server_name + "/api/explain/{}/graphics".format(self.model_id), headers=self.headers, json=json)

        if response.ok:
            return ExpaiExplanation(model_id=self.model_id,
                                    project_id=self.project_id,
                                    sample_id=sample_id,
                                    access_token=self.access_token,
                                    headers=self.headers,
                                    server_name=self.server_name,
                                    session=self.sess,
                                    project=self.project,
                                    raw_values=response.json()['raw_values'],
                                    visualizations=response.json()['visualizations'],
                                    explanation_type_id=explanation_types['Explicación del modelo'],
                                    json_details=json)
        else:
            return generate_response(response, ['visualizations'])

    def explain_variable_effect(self, sample_name: str = None, sample_id: str = None, subset_indexes: list = None, variables: list = None,
                                variables_type: dict = None, target_class: str = None):
        assert sample_name is not None or sample_id is not None, "You must provide a sample name or id for the explanation"
        assert variables is not None, "You must provide the name of a variable to be explored"

        if variables_type is None:
            logging.warning("You didn't specify any type for the variables. We will assume all of them are numerical.")

        if sample_id is None:
            sample_id = self._get_sample_id_from_name(sample_name)

            if sample_id is None:
                logging.error(
                    "We could not find any sample matching that name. Please, try again or use sample_id as parameter")
                return None

        json = {
            "sample_id": sample_id,
            "variables": variables,
            "variables_type": variables_type,
            "subset_indexes": subset_indexes,
            "target_class": target_class
        }

        response =  self.sess.post(self.server_name + "/api/explain/{}/variable/graphics".format(self.model_id), headers=self.headers, json=json)

        if response.ok:
            return ExpaiExplanation(model_id=self.model_id,
                                    project_id=self.project_id,
                                    sample_id=sample_id,
                                    access_token=self.access_token,
                                    headers=self.headers,
                                    server_name=self.server_name,
                                    session=self.sess,
                                    project=self.project,
                                    raw_values=response.json()['raw_values'],
                                    visualizations=response.json()['visualizations'],
                                    explanation_type_id=explanation_types['Explicación de la variable'],
                                    json_details=json)
        else:
            return generate_response(response, ['visualizations'])

    def explain_sample(self, sample_name: str = None, sample_id: str = None, index: list = None, subset_indexes: list = None, target_class: str = None):
        assert sample_name is not None or sample_id is not None, "You must provide a sample name or id for the explanation"
        assert index is not None, "You must specify the index of the sample you want to explain"

        if sample_id is None:
            sample_id = self._get_sample_id_from_name(sample_name)

            if sample_id is None:
                logging.error(
                    "We could not find any sample matching that name. Please, try again or use sample_id as parameter")
                return None

        json = {
            "sample_id": sample_id,
            "index": [index],
            "target_class": target_class,
            "subset_indexes": subset_indexes
        }

        response =  self.sess.post(self.server_name + "/api/explain/{}/sample/graphics".format(self.model_id), headers=self.headers, json=json)

        if response.ok:
            return ExpaiExplanation(model_id=self.model_id,
                                    project_id=self.project_id,
                                    sample_id=sample_id,
                                    access_token=self.access_token,
                                    headers=self.headers,
                                    server_name=self.server_name,
                                    session=self.sess,
                                    project=self.project,
                                    raw_values=response.json()['raw_values'],
                                    visualizations=response.json()['visualizations'],
                                    explanation_type_id=explanation_types['Explicación de la muestra'],
                                    json_details=json)
        else:
            return generate_response(response, ['visualizations'])

    def what_if(self,
                sample_name: str = None,
                sample_id: str = None,
                index: int = None,
                subset_indexes: list = None,
                variables: list = None,
                variables_type: dict = None,
                target_class: str = None):

        assert sample_name is not None or sample_id is not None, "You must provide a sample name or id for the explanation"
        assert all(type_ in ['numerical', 'categorical'] for type_ in variables_type.values()), "You provided an unspported variable type. Please, use numerical or categorical.".format(variables_type)

        if variables_type is None:
            logging.warning("You didn't specify any type for the variables. We will assume all of them are numerical.")

        if sample_id is None:
            sample_id = self._get_sample_id_from_name(sample_name)

            if sample_id is None:
                logging.error(
                    "We could not find any sample matching that name. Please, try again or use sample_id as parameter")
                return None

        json = {
            "sample_id": sample_id,
            "index": [index],
            "subset_indexes": subset_indexes,
            "variables": variables,
            "variables_type": variables_type,
            "target_class": target_class,
        }

        response =  self.sess.post(self.server_name + "/api/explain/{}/what_if".format(self.model_id), headers=self.headers, json=json)

        if response.ok:
            return ExpaiExplanation(model_id=self.model_id,
                                    project_id=self.project_id,
                                    sample_id=sample_id,
                                    access_token=self.access_token,
                                    headers=self.headers,
                                    server_name=self.server_name,
                                    session=self.sess,
                                    project=self.project,
                                    raw_values=response.json()['raw_values'],
                                    visualizations=response.json()['visualizations'],
                                    explanation_type_id=explanation_types['What If'],
                                    json_details=json)
        else:
            return generate_response(response, ['visualizations'])

    def what_if_battle(self,
                       sample_name: str = None,
                       sample_id: str = None,
                       index: int = None,
                       subset_indexes: list = None,
                       replace_dict: dict = None,
                       display_replace_dict: dict = None,
                       target_class: str = None):

        assert sample_name is not None or sample_id is not None, "You must provide a sample name or id for the explanation"
        assert index is not None, "You must provide an index for the sample you want to explore"

        if sample_id is None:
            sample_id = self._get_sample_id_from_name(sample_name)

            if sample_id is None:
                logging.error(
                    "We could not find any sample matching that name. Please, try again or use sample_id as parameter")
                return None

        json = {
            "sample_id": sample_id,
            "index": [index],
            "subset_indexes": subset_indexes,
            "replace_dict": replace_dict,
            "display_replace_dict": display_replace_dict,
            "target_class": target_class,
        }

        response =  self.sess.post(self.server_name + "/api/explain/{}/what_if_battle".format(self.model_id), headers=self.headers, json=json)

        if response.ok:
            return ExpaiExplanation(model_id=self.model_id,
                                    project_id=self.project_id,
                                    sample_id=sample_id,
                                    access_token=self.access_token,
                                    headers=self.headers,
                                    server_name=self.server_name,
                                    session=self.sess,
                                    project=self.project,
                                    raw_values=response.json()['raw_values'],
                                    visualizations=response.json()['visualizations'],
                                    explanation_type_id=explanation_types['What If Battle'],
                                    json_details=json)
        else:
            return generate_response(response, ['visualizations'])
