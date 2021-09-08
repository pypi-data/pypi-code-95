from blaugue.user import BlaugueUser
from blaugue.base import BlaugueBase
import markdown


class BlauguePost:

    def __init__(self, infos: dict, base: BlaugueBase):
        self.infos = infos
        self.base = base

    @property
    def title(self):
        return self.infos['titre']

    @property
    def subtitle(self):
        return self.infos['commentaire']

    @property
    def html_content(self):
        return markdown.markdown(self.infos['contenu'])

    @property
    def markdown_content(self):
        return self.infos['contenu']

    @property
    def image(self):
        return self.infos['image']

    @property
    def book(self):
        return self.infos['book']

    @property
    def id(self):
        return self.infos['_id']

    @property
    def url(self):
        return 'http://blaugue.camponovo.xyz/post/' + self.infos['_id']

    @property
    def author(self):
        return BlaugueUser(self.base.request(self.base.user_url.format(self.infos['user'])).json(), self.base)

    @property
    def type(self):
        return self.infos['type']

    @property
    def comments(self):
        return self.infos['comments']
