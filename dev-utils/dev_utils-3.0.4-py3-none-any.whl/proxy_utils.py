import requests
import json
import random
import time


class Proxy:
    def __init__(self, domain, company_name, ip_type, token, region=None):
        self.token = token
        self.name = company_name
        self.klass = ip_type
        self.company_domain = domain
        self.payload = self.login()
        if not isinstance(self.payload, dict):
            raise Exception("proxy login failed,{}".format(self.payload))
        self.domain = self.payload.get("domain")
        self.port = self.payload.get("port")
        self.username = self.payload.get("username")
        self.password = self.payload.get("password")
        self.region = region

    def login(self):
        retry = 10
        msg = None
        while retry:
            resp = requests.get(
                url="http://{}/ipproxy/getip?ipCompany={}&ipType={}".format(self.company_domain, self.name, self.klass),
                headers={
                    "token": self.token
                })
            text = resp.text
            try:
                payload = json.loads(text).get("payload") or {}
                assert payload.get("domain") and payload.get("port")
                return payload
            except Exception as e:
                time.sleep(2)
                msg = "RespText:{},{}".format(text, e)
                print(msg)
                retry -= 1
        return msg

    @property
    def lum(self):
        assert self.region is not None and self.name is "lum" and self.klass is "datacenter"
        region = [self.region] if isinstance(self.region, str) else self.region
        _path = "https://{username}-country-{region}-session-{session_id}:{password}" \
                "@{domain}:{port}".format(session_id=random.randint(1, 1000000000),
                                          username=self.username,
                                          region=random.choice(region),
                                          password=self.password,
                                          domain=self.domain,
                                          port=self.port,
                                          )
        return {"https": _path,
                "http": _path}

    @property
    def residential(self):
        assert self.region is not None and self.name is "lum" and self.klass is "residential"
        region = [self.region] if isinstance(self.region, str) else self.region
        _path = "https://{username}-country-{region}-session-{session_id}:{password}" \
                "@{domain}:{port}".format(session_id=random.randint(1, 1000000000),
                                          username=self.username,
                                          region=random.choice(region),
                                          password=self.password,
                                          domain=self.domain,
                                          port=self.port,
                                          )
        return {"https": _path,
                "http": _path}

    @property
    def smart(self):
        assert self.name is "smart" and self.klass is "datacenter"
        _path = "https://{username}:{password}@{domain}:{port}".format(
            username=self.username,
            password=self.password,
            domain=self.domain,
            port=self.port,
        )
        return {"https": _path,
                "http": _path.replace("https", "http")}
