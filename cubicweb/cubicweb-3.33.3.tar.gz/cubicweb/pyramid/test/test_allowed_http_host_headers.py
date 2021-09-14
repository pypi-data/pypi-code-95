from cubicweb.pyramid.test import PyramidCWTest
from cubicweb.devtools.testlib import CubicWebTC


class AllowedHTTPHostHeadersTest(PyramidCWTest, CubicWebTC):
    settings = {"cubicweb.bwcompat": True}

    def setUp(self):
        super().setUp()
        self.config["allowed-http-host-headers"] = "localhost,.locahost,127.0.0.1"

    @classmethod
    def init_config(cls, config):
        super().init_config(config)
        cls.cw_config = config

    def test_can_access_in_debug_mode(self):
        self.webapp.get("/")

    def test_cannot_access_without_debug_mode(self):
        self.config["allowed-http-host-headers"] = ""
        self.webapp.get("/", status=403)

    def test_cannot_access_bad_host(self):
        self.webapp.get("/", headers={"Host": "example.com"}, status=403)

    def test_cannot_access_bad_x_host(self):
        self.webapp.get("/", headers={"X-Forwarded-Host": "localhost", "Host": ""})
        self.webapp.get(
            "/", headers={"X-Forwarded-Host": "example.com", "Host": ""}, status=403
        )

    def test_can_access_with_custom_host(self):
        self.config["allowed-http-host-headers"] = "example.com"
        self.webapp.get("/", headers={"Host": "example.com"})

    def test_can_access_with_custom_x_forwarded_host(self):
        self.config["allowed-http-host-headers"] = "example.com"
        self.webapp.get("/", headers={"X-Forwarded-Host": "example.com", "Host": ""})

    def test_x_forwarded_host_other_host_header(self):
        self.config["allowed-http-host-headers"] = "localhost"
        self.webapp.get(
            "/",
            headers={"X-Forwarded-Host": "example.com", "Host": "localhost"},
            status=403,
        )

        self.webapp.reset()
        self.config["allowed-http-host-headers"] = "example.com"
        self.webapp.get(
            "/", headers={"X-Forwarded-Host": "example.com", "Host": "localhost"}
        )

    def test_stars(self):
        self.config["allowed-http-host-headers"] = "*"
        self.webapp.get("/")
        self.webapp.get("/", headers={"Host": "example.com"})
        self.webapp.get("/", headers={"X-Forwarded-Host": "example.com"})
        self.webapp.get("/", headers={"Host": "cubicweb.org"})
        self.webapp.get("/", headers={"X-Forwarded-Host": "cubicweb.org"})

    def test_wildcard(self):
        self.config["allowed-http-host-headers"] = ".localhost"
        self.webapp.get("/", headers={"Host": "localhost"})
        self.webapp.get("/", headers={"Host": "data.localhost"})
        self.webapp.get("/", headers={"Host": "static.localhost"})
