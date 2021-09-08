

class BlaugueUser:

    def __init__(self, infos: dict, base: object):
        self.infos = infos
        self.base = base

    @property
    def name(self):
        return self.infos['name']

    @property
    def id(self):
        return self.infos['_id']

    @property
    def avatar(self):
        return self.base.baseurl + self.infos['pp'] if self.infos['pp'] is not None else 'No avatar'

    @property
    def premium(self):
        return self.infos['premium']

    @property
    def premium_icon(self):
        return self.base.baseurl + self.infos['prem_url']

    @property
    def badges(self):
        return self.infos['badges'].split(', ')

    @property
    def description(self):
        return self.infos['desc']

    @property
    def url(self):
        return 'http://blaugue.camponovo.xyz/user/' + self.infos['name']

    @property
    def bot(self):
        return self.infos['bot']
