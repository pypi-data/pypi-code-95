from blaugue.base import BlaugueBase


class BlaugueBot(BlaugueBase):

    def __init__(self, **bot):
        super().__init__(bot['name'], bot['token'])
        self.base = super()
        self.bot_name = bot['name']
        self.bot_token = bot['token']

