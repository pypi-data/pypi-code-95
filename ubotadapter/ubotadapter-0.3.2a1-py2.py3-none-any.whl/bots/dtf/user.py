from deteefapi import DeteefAPI
from deteefapi.webhook import CommentCreator

from ubotadapter.user import User


class DTFUser(User):
    @property
    def data(self) -> CommentCreator:
        return super()._data

    def get_visual_name(self) -> str:
        return self.data.name

    def get_short_name(self) -> str:
        return self.data.name

    @property
    def id_url(self) -> str:
        return DeteefAPI.get_user_url(self.data.id, self.visual_name)
