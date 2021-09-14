from cubicweb.pyramid.test import PyramidCWTest


def simple_test_view(request):
    return request.response


class PredicatesTC(PyramidCWTest):

    def includeme(self, config):
        # to test route predicate
        config.add_route(
            'permission-update-route',
            r'/{eid}/test-permission-update-route',
            has_cw_permission="update",
        )
        config.add_view(simple_test_view, route_name='permission-update-route')
        # to test view predicate
        config.add_route('permission-update-view', r'/{eid}/test-permission-update-view')
        config.add_view(
            simple_test_view, route_name='permission-update-view', has_cw_permission="update"
        )

    def test_has_cw_permission_route_predicate(self):
        with self.admin_access.repo_cnx() as cnx:
            eid = self.create_user(cnx, "Fernestin").eid
            cnx.commit()
        res = self.webapp.get(f"/{eid}/test-permission-update-route", status='*')
        self.assertEqual(res.status_int, 404)
        self.webapp.post('/login', {
            '__login': self.admlogin, '__password': self.admpassword
        })
        res = self.webapp.get(f"/{eid}/test-permission-update-route", status='*')
        self.assertEqual(res.status_int, 200)

    def test_has_cw_permission_view_predicate(self):
        with self.admin_access.repo_cnx() as cnx:
            eid = self.create_user(cnx, "Fernestin").eid
            cnx.commit()
        res = self.webapp.get(f"/{eid}/test-permission-update-view", status='*')
        self.assertEqual(res.status_int, 404)
        self.webapp.post('/login', {
            '__login': self.admlogin, '__password': self.admpassword
        })
        res = self.webapp.get(f"/{eid}/test-permission-update-view", status='*')
        self.assertEqual(res.status_int, 200)
