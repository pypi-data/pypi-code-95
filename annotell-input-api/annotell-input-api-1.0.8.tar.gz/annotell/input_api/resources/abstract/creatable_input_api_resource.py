import logging
from typing import Optional, Dict, List

import annotell.input_api.model as IAM
from annotell.input_api.file_resource_client import FileResourceClient
from annotell.input_api.http_client import HttpClient
from annotell.input_api.util import get_image_dimensions

log = logging.getLogger(__name__)


class CreateableInputAPIResource(FileResourceClient):

    def __init__(self, client: HttpClient, file_resource_client: FileResourceClient):
        super().__init__()
        self._client = client
        self._file_resource_client = file_resource_client

    def _post_input_request(self, resource_path: str,
                            input_request: dict,
                            project: Optional[str],
                            batch: Optional[str],
                            annotation_types: Optional[List[str]] = None,
                            dryrun: bool = False) -> Optional[IAM.InputJobCreated]:
        """
        Send input to Input API. if not dryrun is true, only validation is performed
        Otherwise, returns `InputJobCreated`
        """
        if annotation_types:
            input_request['annotationTypes'] = annotation_types

        log.debug("POST:ing to %s input %s", resource_path, input_request)

        request_url = self._resolve_request_url(resource_path, project, batch)
        json_resp = self._client.post(
            request_url, json=input_request, dryrun=dryrun)
        if not dryrun:
            response = IAM.InputJobCreated.from_json(json_resp)

            if (len(response.files) > 0):
                self._file_resource_client.upload_files(response.files)
                self._client.post(
                    f"v1/inputs/input-jobs/{response.input_uuid}/commit",
                    json=False,
                    discard_response=True
                )

            return response

    @staticmethod
    def _resolve_request_url(resource_path: str,
                             project: Optional[str] = None,
                             batch: Optional[str] = None) -> str:
        """
        Resolves which request url to use for input based on if project and batch is specified
        """
        url = f"v1/inputs/"

        if project is not None:
            url += f"project/{project}/"
            if batch is not None:
                url += f"batch/{batch}/"

        url += resource_path

        return url
