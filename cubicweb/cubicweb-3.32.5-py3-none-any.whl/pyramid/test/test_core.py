from pyramid.config import Configurator

from cubicweb.pyramid.test import PyramidCWTest
from cubicweb.pyramid.core import includeme

from cubicweb.view import View
from cubicweb.web import Redirect
from cubicweb import ValidationError, NoResultError


class Redirector(View):
    __regid__ = "redirector"

    def call(self, rset=None):
        self._cw.set_header("Cache-Control", "no-cache")
        raise Redirect("http://example.org")


def put_in_uncommitable_state(request):
    try:
        request.cw_cnx.execute('SET U login NULL WHERE U login "anon"')
    except ValidationError:
        pass
    request.response.body = b"OK"
    return request.response


class CoreTest(PyramidCWTest):
    anonymous_allowed = True
    settings = {"cubicweb.bwcompat": True}

    def includeme(self, config):
        config.add_route("uncommitable", "/uncommitable")
        config.add_view(put_in_uncommitable_state, route_name="uncommitable")

    def test_cw_to_pyramid_copy_headers_on_redirect(self):
        self.vreg.register(Redirector)
        try:
            res = self.webapp.get("/?vid=redirector", expect_errors=True)
            self.assertEqual(res.status_int, 303)
            self.assertEqual(res.headers["Cache-Control"], "no-cache")
        finally:
            self.vreg.unregister(Redirector)

    def test_uncommitable_cnx(self):
        res = self.webapp.get("/uncommitable")
        self.assertEqual(res.text, "OK")
        self.assertEqual(res.status_int, 200)

    def test_register_anonymous_user(self):
        new_login = "anon2"

        # Make sure the user is not defined yet
        with self.admin_access.cnx() as cnx:
            new_anon = cnx.find("CWUser", login=new_login)
            with self.assertRaises(NoResultError):
                cnx.find("CWUser", login=new_login).one()

        settings = {
            "cubicweb.bwcompat": False,
            "cubicweb.session.secret": "test",
        }
        config = Configurator(settings=settings)
        config.registry["cubicweb.repository"] = self.repo
        config.registry["cubicweb.config"] = self.config

        # Simulates changing anon in the all-in-one by changing the ApptestConfiguration used during
        self.config.anonymous_credential = (new_login, "password")

        # Simulates instance restart (i.e. pyramid.core.include is called)
        includeme(config)

        with self.admin_access.cnx() as cnx:
            # This raises if the user does not exist
            new_anon = cnx.find("CWUser", login=new_login).one()

            self.assertEquals(config.registry["cubicweb.anonymous_eid"], new_anon.eid)
            # Erase the user to keep a clean database
            new_anon.cw_delete()
            cnx.commit()


if __name__ == "__main__":
    from unittest import main

    main()
