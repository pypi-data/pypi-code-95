from enum import Enum, unique


@unique
class EnumOrderStatus(Enum):
    全部成交 = '0'
    部分成交 = '1'  # 部分成交还在队列中
    正撤 = '2'  # 部分成交不在队列中 ,    # 未成交不在队列中 = '4'
    已报 = '3'  # 未成交还在队列中
    已撤 = '5'  # 撤单
    未知 = 'a'  # 未知    尚未触发 = 'b'     已触发 = 'c'
    废单 = 'e'  # 废单
    未报 = 'f'

    def chinese_name(self):
        """

        :return:
        """
        if self == EnumOrderStatus.全部成交:
            return '全部成交'
        elif self == EnumOrderStatus.部分成交:
            return '部分成交'
        elif self == EnumOrderStatus.正撤:
            return '正撤'
        elif self == EnumOrderStatus.已报:
            return '已报'
        elif self == EnumOrderStatus.已撤:
            return '已撤'
        elif self == EnumOrderStatus.未知:
            return '未知'
        elif self == EnumOrderStatus.废单:
            return '废单'
        elif self == EnumOrderStatus.未报:
            return '未报'

    def can_cancel(self):
        """
        是否可以撤单
        :return:
        """
        return self == EnumOrderStatus.未报 or self == EnumOrderStatus.已报 or self == EnumOrderStatus.部分成交
