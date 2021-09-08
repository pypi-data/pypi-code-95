from ubotadapter.user import User


class TelegramUser(User):
    @property
    def data(self) -> dict:
        return super()._data

    def get_visual_name(self) -> str:
        first_name = self.data.get('first_name', '')
        last_name = self.data.get('last_name', None)
        if not first_name and not last_name:
            return self.id_url
        name = f'{first_name} {last_name}' if last_name else first_name
        return name

    def get_short_name(self) -> str:
        return self.data.get('first_name', None) or self.id_url

    @property
    def id_url(self) -> str:
        return f'@id{self.data["id"]}'
