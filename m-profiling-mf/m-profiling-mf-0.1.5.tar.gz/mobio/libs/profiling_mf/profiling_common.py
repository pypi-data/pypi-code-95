import inspect
from enum import Enum


class SocialIdType:
    APP = 1
    GLOBAL = 2
    PAGE = 3


class SocialType:
    FACEBOOK = 1
    ZALO = 2
    INSTAGRAM = 3
    YOUTUBE = 4
    APP = 5
    LINE = 6
    MOBIO_CHAT_TOOL = 7


class DynamicFieldProperty:
    INTEGER = 1
    FLOAT = 4
    STRING = 2
    DATETIME = 3
    DICT = 5
    EMAIL = 6
    PHONE_NUMBER = 7
    GENDER = 8
    RELATIONSHIP_DATA = 9
    RELATION_WITH_CHILDS = 10
    CHILDS = 11
    SOCIAL_TAGS = 12
    SOCIAL_USER = 13
    UDT = 14
    CARDS = 15
    PUSH_ID = 16
    PS = 17

    @classmethod
    def get_all_property(cls):
        attributes = inspect.getmembers(cls, lambda a: not (inspect.isroutine(a)))
        values = [
            a[1]
            for a in attributes
            if not (a[0].startswith("__") and a[0].endswith("__"))
        ]

        print(
            "DynamicFieldProperty::get_all_property: values = %s" % values
        )
        return values


class DisplayType(Enum):
    SINGLE_LINE = "single_line"
    MULTI_LINE = "multi_line"
    DROPDOWN_SINGLE_LINE = "dropdown_single_line"
    DROPDOWN_MULTI_LINE = "dropdown_multi_line"
    RADIO_SELECT = "radio"
    CHECKBOX = "checkbox"
    DATE_PICKER = "date_picker"
    TAGS = "tags"


class Group:
    INFORMATION = "information"
    DEMOGRAPHIC = "demographic"
    ACTIVITY = "activity"
    LOYALTY = "loyalty"
    OTHER = "other"
    DYNAMIC = "dynamic"


DISPLAY_TYPE_IS_LIST_TYPE = [
    DisplayType.MULTI_LINE.value,
    DisplayType.DROPDOWN_MULTI_LINE.value,
    DisplayType.CHECKBOX.value,
    DisplayType.TAGS.value,
]


class EmailValidateStatus:
    Invalid = -1
    Uncheck = 0
    Valid = 1


class PhoneVerifyStatus:
    VerifyFailed = -1
    UnVerify = 0
    Verified = 1


class ProfileHistoryChangeType:
    ADD = "add"
    REMOVE = "remove"
    CHANGE = "change"
