"""
This class is some algorithm for e-commerce coupon including jd and tb platform.
"""
import re
import math
import logging
from decimal import Decimal

__all__ = ['tb_coupon', 'jd_coupon']


def _remove_exponent(num):
    return num.to_integral() if num == num.to_integral() else num.normalize()


def add_price(price: float, man_value: float, reduce_value: float):
    """
    Use full discount coupons to calculate the hand price.
    :param price: goods price
    :param man_value: minimum limit price
    :param reduce_value: discount price
    :return: real price
    """
    num = 1
    if price <= 0:
        return price
    temp_price = price
    while True:
        if temp_price >= man_value:
            break
        num += 1
        temp_price = price * num
    fin_price = ((price * num) - reduce_value) / num
    return fin_price


class TBCoupon(object):
    """
    Use full discount coupons to calculate the hand price of tb
    """

    def __init__(self):
        self.present_price = None
        self.coupon_list = None

    def estimated_hand_price_one(self, present_price, coupon_list):
        """
        Calculate the unit price and estimate the hand price.
        :return: estimate the hand price of unit price
        """
        self.present_price = present_price
        self.coupon_list = coupon_list
        if self.coupon_list is None or self.coupon_list == '':
            return self.present_price
        if isinstance(self.coupon_list, str):
            coupon_list = self.coupon_list.split('|')
        else:
            coupon_list = self.coupon_list
        try:
            present_price = float(self.present_price)
            low_price = present_price
            for info in coupon_list:
                try:
                    if '商品券' in info or '店铺券' in info or '店铺优惠券' in info or '购物券' in info or \
                            ('满' in info and '省' in info) or ('满' in info and '减' in info):
                        if '促销' in info:
                            for items in info.split(':'):
                                if '省' in items:
                                    info = items
                                    break
                        coupon_info = re.findall(r'[0-9]\d*', info)
                        if len(coupon_info) > 2 or len(coupon_info) == 0:
                            continue
                        elif len(coupon_info) == 1:
                            continue
                        else:
                            full_value = int(coupon_info[0])
                            reduce_value = int(coupon_info[1])
                            # Judge the use conditions and preferential prices
                            if full_value < reduce_value:
                                full_value, reduce_value = reduce_value, full_value
                            # The unit price can only be calculated when it meets the use conditions
                            if full_value <= present_price:
                                fin_price = add_price(present_price, full_value, reduce_value)
                                if fin_price < low_price:
                                    low_price = fin_price
                except Exception as e:
                    logging.error(f'calculate tb error, error={e}')
            # Calculate discount information
            fin_discount_price = discount_price = low_price
            for info in coupon_list:
                if '折' in info:
                    try:
                        promotion_info = info.split(':')
                        for promotion_value in promotion_info:
                            if '折' in promotion_value:
                                promotion_a = re.findall(r'-?\d+\.?\d*e?-?\d*?', promotion_value)
                                if len(promotion_a) > 1:
                                    num = promotion_a[0]
                                    sale = promotion_a[1]
                                    if num > sale:
                                        num, sale = sale, num
                                    if int(num) == 1:
                                        if '.' in sale or '。' in sale:
                                            discount_price = low_price * float(sale) / 10
                                        else:
                                            if len(sale) == 1:
                                                discount_price = low_price * float(sale) / 10
                                            else:
                                                discount_price = low_price * float(sale) / 100
                                else:
                                    sale = promotion_a[0]
                                    if '.' in sale or '。' in sale:
                                        discount_price = low_price * float(sale) / 10
                                    else:
                                        if len(sale) == 1:
                                            discount_price = low_price * float(sale) / 10
                                        else:
                                            discount_price = low_price * float(sale) / 100
                                if fin_discount_price > discount_price:
                                    fin_discount_price = discount_price
                                    break
                        break
                    except:
                        pass
            fin_discount_price = abs(fin_discount_price)
            re_price = str(_remove_exponent(Decimal("%.2f" % fin_discount_price)))
            return re_price
        except Exception as e:
            logging.error(f'calculate tb error, error={e}')
            return str(self.present_price)


class JDCoupon(object):
    """
    Use full discount coupons to calculate the hand price of jd
    """

    def __init__(self):
        self.present_price = None
        self.coupon_list = None

    def estimated_hand_price_one(self, present_price, coupon_list):
        """
        Calculate the unit price and estimate the hand price.
        :return: estimate the hand price of unit price
        """
        self.present_price = present_price
        self.coupon_list = coupon_list
        if self.coupon_list is None or self.coupon_list == '':
            return self.present_price
        if isinstance(self.coupon_list, str):
            coupon_list = self.coupon_list.split('|')
        else:
            coupon_list = self.coupon_list
        try:
            present_price = float(self.present_price)
            low_price = present_price
            for info in coupon_list:
                try:
                    if '折' in info:
                        continue
                    if '每满' in info and '减' in info:
                        base_a = re.findall(r'[0-9]\d*', info)
                        if len(base_a) >= 2:
                            _mun = math.floor(present_price / int(base_a[0]))
                            low_value = _mun * float(base_a[1])
                            low_price = present_price - low_value
                            if '最多' in info:
                                max_value = float(base_a[2])
                                if low_value > max_value:
                                    low_price = present_price - max_value
                            assert low_price > 0
                            break
                    if '购满' in info:
                        continue
                    if '商品券' in info or '店铺券' in info or '店铺优惠券' in info or '购物券' in info or \
                            ('满' in info and '省' in info) or ('满' in info and '减' in info):
                        if '促销' in info:
                            for items in info.split(':'):
                                if '省' in items:
                                    info = items
                                    break
                        coupon_info = re.findall(r'[0-9]\d*', info)
                        if len(coupon_info) == 0:
                            continue
                        elif len(coupon_info) == 1:
                            continue
                        else:
                            full_value = int(coupon_info[0])
                            reduce_value = int(coupon_info[1])
                            if full_value < reduce_value:
                                full_value, reduce_value = reduce_value, full_value
                            if full_value <= present_price:
                                fin_price = add_price(present_price, full_value, reduce_value)
                                if fin_price < low_price:
                                    low_price = fin_price
                except Exception as e:
                    logging.error(f'calculate tb error, error={e}')
            fin_discount_price = discount_price = low_price
            for info in coupon_list:
                if '促销' in info or '折' in info:
                    try:
                        promotion_info = info.split(':')
                        for promotion_value in promotion_info:
                            if '折' in promotion_value:
                                promotion_a = re.findall(r'-?\d+\.?\d*e?-?\d*?', promotion_value)
                                if len(promotion_a) > 1:
                                    num = promotion_a[0]
                                    sale = promotion_a[1]
                                    if num > sale:
                                        num, sale = sale, num
                                    if int(num) == 1:
                                        if '.' in sale or '。' in sale:
                                            discount_price = low_price * float(sale) / 10
                                        else:
                                            if len(sale) == 1:
                                                discount_price = low_price * float(sale) / 10
                                            else:
                                                discount_price = low_price * float(sale) / 100
                                else:
                                    sale = promotion_a[0]
                                    if '.' in sale or '。' in sale:
                                        discount_price = low_price * float(sale) / 10
                                    else:
                                        if len(sale) == 1:
                                            discount_price = low_price * float(sale) / 10
                                        else:
                                            discount_price = low_price * float(sale) / 100
                                if fin_discount_price > discount_price:
                                    fin_discount_price = discount_price
                                    break
                    except Exception as e:
                        logging.error(f'calculate tb error, error={e}')
            re_price = str(_remove_exponent(Decimal("%.2f" % fin_discount_price)))
            return re_price
        except Exception as e:
            logging.error(f'calculate tb error, error={e}')
            return str(self.present_price)


tb_coupon = TBCoupon()
jd_coupon = JDCoupon()
