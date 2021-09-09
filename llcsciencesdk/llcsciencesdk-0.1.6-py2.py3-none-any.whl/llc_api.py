from dataclasses import dataclass, field

import requests
import pandas as pd

from llcsciencesdk.exceptions import ApiAuthenticationError, ApiGeneralError, ApiTokenError
from llcsciencesdk.urls import make_urls, ApiUrls


@dataclass
class ScienceSdk:
    auth_token: str = field(default_factory=str, repr=False)
    environment: str = "production"
    api_urls: ApiUrls = None

    def __post_init__(self):
        self.api_urls = make_urls(self.environment)

    def login(self, username: str, password: str):
        r = requests.post(self.api_urls.AUTH_URL, data={"username": username, "password": password})

        if r.status_code == 401:
            raise ApiAuthenticationError(r.text)

        elif not r.ok:
            raise ApiGeneralError(r.text)

        self.auth_token = r.json()["access"]

    def get_model_inputs(self, config_option: int):

        if not self.auth_token:
            raise ApiTokenError

        data = requests.get(
            self.api_urls.GET_MODEL_INPUT_URL + str(config_option),
            headers={"Authorization": f"Bearer {self.auth_token}"},
        )

        site_info = data.json()["site_info"]
        plot_types = data.json()["plot_types"]
        parameter_data = data.json()["parameter_data"]
        parameter_info = data.json()["parameter_info"]
        species_info = data.json()["species_info"]
        model_info = data.json()["model_info"]

        df_sites_info = pd.json_normalize(site_info)
        df_plot_types = pd.json_normalize(plot_types)
        df_parameter_data = pd.json_normalize(parameter_data)
        df_parameter_info = pd.json_normalize(parameter_info)
        df_species_info = pd.json_normalize(species_info)
        df_model_info = pd.json_normalize(model_info)

        return (
            df_sites_info,
            df_plot_types,
            df_parameter_data,
            df_parameter_info,
            df_species_info,
            df_model_info,
        )

    def get_model_inputs_json(self, config_option: int):

        if not self.auth_token:
            raise ApiTokenError

        data = requests.get(
            self.api_urls.GET_MODEL_INPUT_URL + str(config_option),
            headers={"Authorization": f"Bearer {self.auth_token}"},
        )

        result = {
            "site_info": data.json()["site_info"],
            "plot_types": data.json()["plot_types"],
            "parameter_data": data.json()["parameter_data"],
            "parameter_info": data.json()["parameter_info"],
            "species_info": data.json()["species_info"],
            "model_info": data.json()["model_info"],
        }

        return result

    def get_old_model_inputs(self, model_runs: list):
        if not self.auth_token:
            raise ApiTokenError

        list_of_runs = ",".join(map(str, model_runs))
        data = requests.get(
            self.api_urls.GET_OLD_MODEL_INPUT_URL + f"={list_of_runs}",
            headers={"Authorization": f"Bearer {self.auth_token}"},
        )

        sites_info = data.json()["sites_info"]
        parameter_data = data.json()["parameter_data"]
        parameter_info = data.json()["parameter_info"]
        species_info = data.json()["species_info"]
        model_info = data.json()["model_info"]

        df_sites_info = pd.json_normalize(sites_info)
        df_parameter_data = pd.json_normalize(parameter_data)
        df_parameter_info = pd.json_normalize(parameter_info)
        df_species_info = pd.json_normalize(species_info)
        df_model_info = pd.json_normalize(model_info)

        return (
            df_sites_info,
            df_parameter_data,
            df_parameter_info,
            df_species_info,
            df_model_info,
        )
