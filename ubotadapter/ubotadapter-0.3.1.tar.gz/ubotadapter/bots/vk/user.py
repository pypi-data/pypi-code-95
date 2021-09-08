from vkale.items.user_items import UserItem

from ubotadapter.user import User


class VKUser(User):
    @property
    def data(self) -> UserItem:
        return super().data

    def get_visual_name(self) -> str:
        return f'{self.data.first_name} {self.data.last_name}'

    def get_short_name(self) -> str:
        return self.data.first_name

    @property
    def id_url(self) -> str:
        return f'@id{self.uid}'
