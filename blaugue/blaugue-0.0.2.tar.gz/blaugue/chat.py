from blaugue import user


class BlaugueMessage:

    def __init__(self, infos: dict, base: object, chat):
        self.infos = infos
        self.base = base
        self.chat = chat

    @property
    def html_content(self):
        return self.infos['message']

    @property
    def content(self):
        return self.infos['message'].replace('<br>', '').replace('&nbsp;', '')

    @property
    def author(self):
        return user.BlaugueUser(self.base.request(self.base.user_url.format(self.infos['from']['name'])).json(), self.base)

    @property
    def receiver(self):
        if self.chat.id == 'blaugue':
            return [user.BlaugueUser(info, self.base) for info in self.base.request(self.base.user_url.format(self.infos['to'])).json()['users']]
        return user.BlaugueUser(self.base.request(self.base.user_url.format(self.infos['to'])).json(), self.base)


class BlaugueChat:

    def __init__(self, infos: dict, base: object):
        self.infos = infos
        self.base = base

    @property
    def id(self):
        return self.infos['chatname']

    @property
    def name(self):
        name = self.infos['chatname'].split('@')[0]
        try:
            name = name.split('.')[0]
        finally:
            name = name[0].upper() + name[1:]
        return name

    @property
    def messages(self):
        return [BlaugueMessage(mes, self.base, self) for mes in self.infos['messages']]
