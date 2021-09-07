from typing import List, Dict

import annotell.input_api.model.annotation as AnnotationModel
from annotell.input_api.util import filter_none
from annotell.input_api.resources.abstract import InputAPIResource


class AnnotationResource(InputAPIResource):
    def get_annotations(
        self,
        input_uuids: List[str]
    ) -> Dict[str, List[AnnotationModel.Annotation]]:
        """
        Returns the export ready annotations, either
        * All annotations connected to a specific request, if a request id is given
        * All annotations connected to the organization of the user, if no request id is given

        :param input_uuids: List with input uuid
        :param request_id: An id of a request
        :return Dict: A dictionary containing the ready annotations
        """
        external_id_query_param = ",".join(input_uuids) if input_uuids else None
        json_resp = self._client.get("v1/annotations", params=filter_none({
            "inputs": external_id_query_param
        }))


        annotations = dict()
        for k, v in json_resp.items():
            annotations[k] = [
                AnnotationModel.Annotation.from_json(annotation) for annotation in v
            ]
        return annotations
