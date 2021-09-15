import os
from .api_client import APIClientBase


class Jobs(APIClientBase):
    def __init__(self, url_base=None, **kwargs):
        super().__init__(url_base or os.environ.get("PROTECTION_SERVICE", ""), **kwargs)

    def get_jobs(self):
        return self.get_request("/jobs")

    def get_job(self, id: str):
        return self.get_request("/jobs/{id}", id=id)

    def create_job(self, body: dict):
        return self.post_request("/jobs", body=body)

    def patch_job(self, id: str, body: dict):
        return self.patch_request("/jobs/{id}", id=id, body=body)

    def delete_job(self, id: str):
        return self.delete_request("/jobs/{id}", id=id)
