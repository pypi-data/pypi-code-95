from typing import Dict
from urllib.parse import urljoin

from quillbot.api.router import ROUTE


class API:
    def __init__(self, host: str, routes: Dict[str, str]):
        self.host = host
        self.endpoint = {key: urljoin(host, routes[key]) for key in routes}


def get_api(route):
    api = API("http://127.0.0.1:8080/", ROUTE)
    return api.endpoint[route]


def get_headers() -> Dict:
    headers = {
        "Authorization": "public eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJGcHJmb3FKeUdjamNGamdLN1kxLUJTQ0V5Z2JkTDlOWXpscEVaeFJmUng0In0.eyJqdGkiOiIxMzNkYzAwMi04ZDAyLTQ4MTctYWM4MS01MjMxZjY4NDQ3MWUiLCJleHAiOjE1OTA2NjYxMTYsIm5iZiI6MCwiaWF0IjoxNTkwNjY1ODE2LCJpc3MiOiJodHRwczovL2F1dGgudHdudHkuZGUvYXV0aC9yZWFsbXMvVFdOVFkiLCJzdWIiOiIyNjIzNTBlOS0zZmE3LTRjN2ItOWYxZS1jNmEzMzkwNmE1MTIiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJDQ1QiLCJub25jZSI6ImE2M2I2MDIwLWJjYjYtNGJmNS1hM2FhLTk1OTRiMWU2N2MxZCIsImF1dGhfdGltZSI6MTU5MDY2NTgxNiwic2Vzc2lvbl9zdGF0ZSI6ImFkODczMjBmLTVmOTQtNDA3Ni04MzlkLWE5YTQ1MDJjYWY5MyIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiKiJdLCJyZXNvdXJjZV9hY2Nlc3MiOnsiQ0NUIjp7InJvbGVzIjpbInVzZXIiXX19LCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiJSb21hbiBQZXJlc29saWFrIiwicHJlZmVycmVkX3VzZXJuYW1lIjoicm9tYW4iLCJnaXZlbl9uYW1lIjoiUm9tYW4iLCJmYW1pbHlfbmFtZSI6IlBlcmVzb2xpYWsiLCJlbWFpbCI6InBlcmVzb2xpYWtAdHdudHkuZGUifQ.AzmqWwgoDxly4F0tP6kASBmRpyPs_c3gPAu97L6HDrFaYmlkXik2iNKcbjyZMNBvGoLWcO3dLV2OhMTCe_NnauMximQW6Ru92EYYCdu71bFY93VHCEeJGPXXvvoQ-UwVx0JtHGmnGDNT2EaPdTJAdnxzuyUP77f2YwqmNBJnJPST6vN2mCtGgU2r7y6SB3qG5VmgQtBvyT7ofJrwlWIfKj-ul00zvEp_kYw0iCKdZLxkoa3J5s7HyKkSBrNjxldccxeMwbs3nJ4r9MQUXumEJPV33cFBU7VmH7vF9X9-Gfx1lHoGFc-9R41hE_CFs2tIkf2tuGmesAGu_K61kOAu-g_"
    }

    return headers
