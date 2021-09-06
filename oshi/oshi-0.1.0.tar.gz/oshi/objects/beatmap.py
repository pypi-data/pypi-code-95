from __future__ import annotations

import typing
import datetime

from .base import BaseObject


__all__ = ("Beatmap",)


class Beatmap(BaseObject):
    """
    Represents an osu beatmap.

    Attributes:
        acurracy (int): The accuracy of the map.
        ar (int): The approach rate of the map.
        beatmapset (dict): The beatmapset of the map.
        beatmapset_id (int): The id of the beatmapset.
        bpm (int): The bpm/beats per minute of the map.
        checksum (str): The checksum of the map.
        convert: (bool): Whether or not the map is converted.
        count_circles (int): The number of hit circles in the map.
        count_sliders (int): The number of sliders in the map.
        count_spinners (int): The number of spinners in the map.
        cs (float): The circle size of the map.
        deleted_at (typing.Optional[None, datetime.datetime]): The time when the map was deleted at. 0 if not deleted
        difficulty_rating (float): The difficulty rating of the map.
        drain (float): The HP drain of the map.
        failtimes (dict): The failtimes of the map.
        hit_length (int): The hit length of the map.
        is_scoreable (bool): Whether or not the map is scoreable.
        last_updated (datetime.datetime): The latest time of when the map was updated.
        max_combo (int): The max combo of the map.
        mode (str): The mode of the map.
        mode_int (int): The integer version of the mode for the map.
        passcount (int): The number of passes on the map.
        playcount (int): The number of plays on the map.
        ranked (int): The integer version for the status of the map.
        status (str): The status of the map.
        total_length (int) The total length of the map.
        url (str): The URL of the map.
        user_id (int): The user ID of creator.
        version (str): The version of the map.

    """

    __slots__ = (
        "accuracy",
        "ar",
        "beatmapset",
        "beatmapset_id",
        "bpm",
        "checksum",
        "convert",
        "count_circles",
        "count_sliders",
        "count_spinners",
        "cs",
        "difficulty_rating",
        "drain",
        "failtimes",
        "hit_length",
        "is_scoreable",
        "max_combo",
        "mode",
        "mode_int",
        "passcount",
        "playcount",
        "ranked",
        "status",
        "total_length",
        "url",
        "user_id",
        "version",
    )

    @property
    def deleted_at(self) -> typing.Union[int, datetime.datetime]:
        if timestamp := self.data.get("deleted_at"):
            return datetime.datetime.fromtimestamp(timestamp)

        return 0

    @property
    def last_updated(self) -> datetime.datetime:
        return datetime.datetime.strptime(self.data["last_updated"], "%Y-%m-%dT%H:%M:%S%z")
