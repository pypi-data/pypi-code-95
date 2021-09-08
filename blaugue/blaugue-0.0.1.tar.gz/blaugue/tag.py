from blaugue.post import BlauguePost


class BlaugueTag:

    def __init__(self, tag: dict, base: object):
        self.tag = tag
        self.base = base

    @property
    def name(self):
        return self.tag['type']

    @property
    def posts(self):
        return [BlauguePost(tag, self.base) for tag in self.base.request(self.base.search_url.format(self.name)).json()['tags']]

    @property
    def url(self):
        return 'http://blaugue.camponovo.xyz/type/' + self.name
