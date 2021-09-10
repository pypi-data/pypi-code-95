from typing import Optional
import os
from httpx import AsyncClient


class XiqV1Client(AsyncClient):
    DEFAULT_TIMEOUT = 10

    def __init__(self, *vargs, xiq: Optional[dict] = None, **kwargs):
        kwargs.setdefault("base_url", os.environ["XIQ_ADDR"] + "/xapi/v1/")
        kwargs.setdefault("timeout", self.DEFAULT_TIMEOUT)
        super(XiqV1Client, self).__init__(*vargs, **kwargs)

        if xiq:
            self.headers["X-AH-API-CLIENT-SECRET"] = xiq["client_secret"]
            self.headers["X-AH-API-CLIENT-ID"] = xiq["client_id"]
            self.headers["X-AH-API-CLIENT-REDIRECT-URI"] = xiq["redirect_uri"]
            self.headers["Authorization"] = "Bearer " + xiq["token"]
            return

        self.headers["X-AH-API-CLIENT-SECRET"] = os.environ["XIQ_CLIENT_SECRET"]
        self.headers["X-AH-API-CLIENT-ID"] = os.environ["XIQ_CLIENT_ID"]
        self.headers["X-AH-API-CLIENT-REDIRECT-URI"] = os.environ["XIQ_REDIRECT_URI"]
        self.headers["Authorization"] = "Bearer " + os.environ["XIQ_TOKEN"]
