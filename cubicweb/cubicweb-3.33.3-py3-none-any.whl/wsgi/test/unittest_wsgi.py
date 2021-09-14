import webtest.app
from io import BytesIO

from cubicweb.pyramid.test import PyramidCWTest

from cubicweb.wsgi.request import CubicWebWsgiRequest
from cubicweb.multipart import MultipartError


class WSGIAppTC(PyramidCWTest):
    settings = {"cubicweb.bwcompat": True}

    def test_content_type(self):
        r = webtest.app.TestRequest.blank("/", {"CONTENT_TYPE": "text/plain"})

        req = CubicWebWsgiRequest(r.environ, self.vreg)

        self.assertEqual("text/plain", req.get_header("Content-Type"))

    def test_content_body(self):
        r = webtest.app.TestRequest.blank(
            "/",
            {
                "CONTENT_LENGTH": 12,
                "CONTENT_TYPE": "text/plain",
                "wsgi.input": BytesIO(b"some content"),
            },
        )

        req = CubicWebWsgiRequest(r.environ, self.vreg)

        self.assertEqual(b"some content", req.content.read())

    def test_big_content(self):
        content = b"x" * 100001
        r = webtest.app.TestRequest.blank(
            "/",
            {
                "CONTENT_LENGTH": len(content),
                "CONTENT_TYPE": "text/plain",
                "wsgi.input": BytesIO(content),
            },
        )

        req = CubicWebWsgiRequest(r.environ, self.vreg)

        self.assertEqual(content, req.content.read())

    def test_post(self):
        self.webapp.post(
            "/", params={"__login": self.admlogin, "__password": self.admpassword}
        )

    def test_post_bad_form(self):
        # XXX moving to PyramidCWTest we don't even reach CW code here because
        # it crashes before in webob code so we can't have a MultipartError
        # and we get a ValueError instead, I'm not sure it's the thing we want
        #
        # with self.assertRaises(MultipartError):

        with self.assertRaises(ValueError):
            self.webapp.post(
                "/",
                params="badcontent",
                headers={"Content-Type": "multipart/form-data"},
            )

    def test_post_non_form(self):
        csrf_token = self.webapp.get("/login").form.fields["csrf_token"][0].value

        self.webapp.post(
            "/",
            params={},
            headers={"Content-Type": "application/json", "X-CSRF-Token": csrf_token},
        )

    def test_get_multiple_variables(self):
        r = webtest.app.TestRequest.blank("/?arg=1&arg=2")
        req = CubicWebWsgiRequest(r.environ, self.vreg)

        self.assertEqual(["1", "2"], req.form["arg"])

    def test_post_multiple_variables(self):
        r = webtest.app.TestRequest.blank("/", POST="arg=1&arg=2")
        req = CubicWebWsgiRequest(r.environ, self.vreg)

        self.assertEqual(["1", "2"], req.form["arg"])

    def test_post_files(self):
        content_type, params = self.webapp.encode_multipart(
            (), (("filefield", "aname", b"acontent"),)
        )
        r = webtest.app.TestRequest.blank("/", POST=params, content_type=content_type)
        req = CubicWebWsgiRequest(r.environ, self.vreg)
        self.assertIn("filefield", req.form)
        fieldvalue = req.form["filefield"]
        self.assertEqual("aname", fieldvalue[0])
        self.assertEqual(b"acontent", fieldvalue[1].read())

    def test_post_unicode_urlencoded(self):
        params = "arg=%C3%A9"
        r = webtest.app.TestRequest.blank(
            "/", POST=params, content_type="application/x-www-form-urlencoded"
        )
        req = CubicWebWsgiRequest(r.environ, self.vreg)
        self.assertEqual("é", req.form["arg"])


if __name__ == "__main__":
    import unittest

    unittest.main()
