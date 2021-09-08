from enum import Enum, unique


@unique
class EnumOrderSubmitStatus(Enum):
    insert_submitted = '0'
    cancel_submitted = '1'
    modify_submitted = '2'
    accepted = '3'
    insert_rejected = '4'
    cancel_rejected = '5'
    modify_rejected = '6'
    un_known = '-1'
