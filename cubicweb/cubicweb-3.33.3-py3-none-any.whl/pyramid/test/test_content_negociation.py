from rdflib import Graph

from cubicweb.pyramid.test import PyramidCWTest

_MIMETYPES = [
    "application/rdf+xml",
    "text/turtle",
    "text/n3",
    "application/n-quads",
    "application/n-triples",
    "application/trig",
    "application/ld+json",
]


class ContentNegociationTC(PyramidCWTest):

    # necessary to allow the request to reach cubicweb if pyramid is 404
    settings = {"cubicweb.bwcompat": True}

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            self.blog_entry = cnx.create_entity(
                "BlogEntry", title="une news !", content="cubicweb c'est beau"
            )
            cnx.commit()

    def test_content_negociation_link_alternate(self):
        self.login()
        res = self.webapp.get(f"/BlogEntry/{self.blog_entry.eid}")
        links = res.headers.getall("Link")
        for mimetype in _MIMETYPES:
            assert (
                f"<http://testing.fr/cubicweb/{self.blog_entry.eid}>;"
                f"rel=alternate;type={mimetype}"
            ) in links

    def test_content_negociation_triples_content(self):
        self.login()
        res = self.webapp.get(
            f"/BlogEntry/{self.blog_entry.eid}", headers={"Accept": "text/n3"}
        )
        g = Graph()
        g.parse(data=res.body.decode("utf-8"), format="text/n3")
        ask_res = g.query(
            f"""
            ASK {{
                <http://testing.fr/cubicweb/{self.blog_entry.eid}>
                    a <http://ns.cubicweb.org/cubicweb/0.0/BlogEntry>;
                    <http://ns.cubicweb.org/cubicweb/0.0/title> "{self.blog_entry.title}";
                    <http://ns.cubicweb.org/cubicweb/0.0/content> "{self.blog_entry.content}".
            }}"""
        )
        assert ask_res.askAnswer
