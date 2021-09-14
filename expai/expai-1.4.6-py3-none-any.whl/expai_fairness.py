import logging
from IPython.core.display import display, HTML
from expai.utils import generate_response
import numpy as np


class ExpaiModelFairness:
    def __init__(self, model_id: str, project_id: str, access_token: str, headers: dict, server_name: str, session, project):
        self.model_id = model_id
        self.project_id = project_id

        self.server_name = server_name
        self.access_token = access_token

        self.headers = headers

        self.sess = session
        self.project = project

    def launch_fairness_dashboard(self, sample_name: str = None, sample_id: str = None, subset_indexes: list = None, protected_columns: list = None):
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
            "protected_columns": ",".join(protected_columns) if protected_columns else None,
            "get_html": True
        }

        response = self.sess.request("POST",
                                     self.server_name + "/api/fairness/{}/dashboard".format(self.model_id),
                                     headers=self.headers, json=json)

        if response.ok:
            display(HTML("<a blank href='{}'>Click here to open the dashboard</a>".format(response.json()['dashboard_url'])))
            return response.json()['dashboard_url']
        else:
            return generate_response(response, ['html'])


    def _get_sample_id_from_name(self, sample_name: str = None):
        sample_list = self.project.sample_list()
        sample_list = sample_list.get('samples')

        if sample_list is None:
            return None

        for sample in sample_list:
            if sample['sample_name_des'] == sample_name:
                return sample['sample_id']
        return None
