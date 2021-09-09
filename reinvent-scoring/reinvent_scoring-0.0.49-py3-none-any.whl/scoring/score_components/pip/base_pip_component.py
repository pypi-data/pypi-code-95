import asyncio
import json
import os
from abc import abstractmethod
from typing import List

import aiohttp
# import nest_asyncio
import numpy as np
import rdkit.Chem as rkc

from reinvent_scoring.scoring.component_parameters import ComponentParameters
from reinvent_scoring.scoring.score_components import BaseScoreComponent
from reinvent_scoring.scoring.score_summary import ComponentSummary
from reinvent_scoring.scoring.score_transformations import TransformationFactory
from reinvent_scoring.scoring.enums import TransformationTypeEnum, EnvironmentalVariablesEnum


# nest_asyncio.apply()


class BasePiPComponent(BaseScoreComponent):
    def __init__(self, parameters: ComponentParameters):
        super().__init__(parameters)
        self._environment_keys = EnvironmentalVariablesEnum()
        self.transformation_function = self._assign_transformation(self.parameters.specific_parameters)
        self._request_url = self._create_url(self.parameters.component_type)
        self._request_header = self._create_header()

    def calculate_score(self, molecules: List[rkc.Mol]) -> ComponentSummary:
        valid_smiles = self._chemistry.mols_to_smiles(molecules)
        score, raw_score = self._calculate_score(valid_smiles)
        score_summary = ComponentSummary(total_score=score, parameters=self.parameters, raw_score=raw_score)
        return score_summary

    def _calculate_score(self, smiles: List[str]) -> np.array:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._post_batch(self._request_url, smiles, self._request_header))

        results_raw = self._parse_multicompound_result(response, len(smiles))
        results = self._transformed_results(results_raw)
        return results, results_raw

    def _parse_multicompound_result(self, response_json: dict, data_size: int) -> np.array:
        compounds = response_json['jsonData'][0]["Compounds"]

        results_raw = np.empty(data_size, dtype=np.float32)
        results_raw[:] = np.nan

        try:
            for compound in compounds:
                try:
                    index = int(compound["Compound"])
                    results_raw[index] = self._parse_compound(compound)

                except (ValueError, TypeError, KeyError):
                    # ValueError: float("a")
                    # TypeError: 3["anything"]
                    # KeyError: compound["bad-name"]
                    pass  # If parsing failed, keep value NaN for this compound and continue.
        finally:
            return results_raw

    def _transformed_results(self, results_raw: np.array) -> np.array:
        """Returns np.array with non-NaN elements transformed by transformation function, and all NaN elements
        transformed into 0. """
        valid_mask = ~np.isnan(results_raw)
        results_raw_valid = results_raw[valid_mask]
        results_transformed = self.transformation_function(results_raw_valid, self.parameters.specific_parameters)
        results = np.zeros(len(results_raw), dtype=np.float32)
        results[valid_mask] = results_transformed
        return results

    def _create_url(self, component_name) -> str:
        pip_url = self._get_enviornment_variable(self._environment_keys.PIP_URL)
        request_url = pip_url.format(component_name)
        return request_url

    def _create_header(self) -> dict:
        pip_key = self._get_enviornment_variable(self._environment_keys.PIP_KEY)

        header = {'Content-Type': 'application/json', 'x-api-key': pip_key}
        return header

    async def _post_request(self, request_url, data, header) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(request_url, json=data, headers=header) as response:
                return await response.json()

    async def _post_batch(self, url, smiles, header):
        data = self._format_data(smiles)
        result = await self._post_request(url, data, header)
        return result

    @abstractmethod
    def _parse_compound(self, compound):
        pass

    def _format_data(self, smiles: List[str]) -> dict:
        lines = [f"{smi} {i}" for i, smi in enumerate(smiles)]
        joined_lines = "\n".join(lines)
        data = {
            "jsonData": {
                "smiles": joined_lines
            }
        }
        return data

    def _assign_transformation(self, specific_parameters: {}):
        transformation_type = TransformationTypeEnum()
        factory = TransformationFactory()
        if self.parameters.specific_parameters[self.component_specific_parameters.TRANSFORMATION]:
            transform_function = factory.get_transformation_function(specific_parameters)
        else:
            self.parameters.specific_parameters[
                self.component_specific_parameters.TRANSFORMATION_TYPE] = transformation_type.NO_TRANSFORMATION
            transform_function = factory.no_transformation
        return transform_function

    def _retrieve_pip_key_from_config(self, variable: str) -> str:
        try:
            project_root = os.path.dirname(__file__)
            with open(os.path.join(project_root, '../../../configs/config.json'), 'r') as f:
                config = json.load(f)
            is_dev = config[variable]
            return is_dev
        except KeyError as ex:
            raise KeyError(f"Key {variable} not found in reinvent_scoring/configs/config.json")

    def _get_enviornment_variable(self, variable: str) -> str:
        try:
            return os.environ[variable]
        except KeyError:
            return self._retrieve_pip_key_from_config(variable)
