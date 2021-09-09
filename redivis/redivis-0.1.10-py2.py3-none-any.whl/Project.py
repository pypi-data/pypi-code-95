from redivis import Query


class Project:
    def __init__(self, name, *, user, properties=None):
        self.user = user
        self.name = name
        self.uri = f"/projects/{self.user.name}.{self.name}"
        self.properties = properties

    def query(self, query):
        return Query(query, default_project=self)
