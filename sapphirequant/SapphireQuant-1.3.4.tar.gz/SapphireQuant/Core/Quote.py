
class Quote:
    """
    行情
    """
    def __init__(self):
        self._askPrice = [0.0] * 10
        self._askVolume = [0] * 10
        self._bidPrice = [0.0] * 10
        self._bidVolume = [0] * 10

        self.bid_num_order1 = 0
        self.bid_num_order2 = 0
        self.bid_num_order3 = 0
        self.bid_num_order4 = 0
        self.bid_num_order5 = 0
        self.bid_num_order6 = 0
        self.bid_num_order7 = 0
        self.bid_num_order8 = 0
        self.bid_num_order9 = 0
        self.bid_num_order10 = 0

        self.ask_num_order1 = 0
        self.ask_num_order2 = 0
        self.ask_num_order3 = 0
        self.ask_num_order4 = 0
        self.ask_num_order5 = 0
        self.ask_num_order6 = 0
        self.ask_num_order7 = 0
        self.ask_num_order8 = 0
        self.ask_num_order9 = 0
        self.ask_num_order10 = 0

    @property
    def ask_price(self):
        return self._askPrice

    @property
    def ask_volume(self):
        return self._askVolume

    @property
    def bid_price(self):
        return self._bidPrice

    @property
    def bid_volume(self):
        return self._bidVolume

    @property
    def ask_price1(self):
        return self.ask_price[0]

    @ask_price1.setter
    def ask_price1(self, value):
        self.ask_price[0] = value

    @property
    def ask_price2(self):
        return self.ask_price[1]

    @ask_price2.setter
    def ask_price2(self, value):
        self.ask_price[1] = value

    @property
    def ask_price3(self):
        return self.ask_price[2]

    @ask_price3.setter
    def ask_price3(self, value):
        self.ask_price[2] = value

    @property
    def ask_price4(self):
        return self.ask_price[3]

    @ask_price4.setter
    def ask_price4(self, value):
        self.ask_price[3] = value

    @property
    def ask_price5(self):
        return self.ask_price[4]

    @ask_price5.setter
    def ask_price5(self, value):
        self.ask_price[4] = value

    @property
    def ask_price6(self):
        return self.ask_price[5]

    @ask_price6.setter
    def ask_price6(self, value):
        self.ask_price[5] = value

    @property
    def ask_price7(self):
        return self.ask_price[6]

    @ask_price7.setter
    def ask_price7(self, value):
        self.ask_price[6] = value

    @property
    def ask_price8(self):
        return self.ask_price[7]

    @ask_price8.setter
    def ask_price8(self, value):
        self.ask_price[7] = value

    @property
    def ask_price9(self):
        return self.ask_price[8]

    @ask_price9.setter
    def ask_price9(self, value):
        self.ask_price[8] = value

    @property
    def ask_price10(self):
        return self.ask_price[9]

    @ask_price10.setter
    def ask_price10(self, value):
        self.ask_price[9] = value

    @property
    def ask_volume1(self):
        return self.ask_volume[0]

    @ask_volume1.setter
    def ask_volume1(self, value):
        self.ask_volume[0] = value

    @property
    def ask_volume2(self):
        return self.ask_volume[1]

    @ask_volume2.setter
    def ask_volume2(self, value):
        self.ask_volume[1] = value

    @property
    def ask_volume3(self):
        return self.ask_volume[2]

    @ask_volume3.setter
    def ask_volume3(self, value):
        self.ask_volume[2] = value

    @property
    def ask_volume4(self):
        return self.ask_volume[3]

    @ask_volume4.setter
    def ask_volume4(self, value):
        self.ask_volume[3] = value

    @property
    def ask_volume5(self):
        return self.ask_volume[4]

    @ask_volume5.setter
    def ask_volume5(self, value):
        self.ask_volume[4] = value

    @property
    def ask_volume6(self):
        return self.ask_volume[5]

    @ask_volume6.setter
    def ask_volume6(self, value):
        self.ask_volume[5] = value

    @property
    def ask_volume7(self):
        return self.ask_volume[6]

    @ask_volume7.setter
    def ask_volume7(self, value):
        self.ask_volume[6] = value

    @property
    def ask_volume8(self):
        return self.ask_volume[7]

    @ask_volume8.setter
    def ask_volume8(self, value):
        self.ask_volume[7] = value

    @property
    def ask_volume9(self):
        return self.ask_volume[8]

    @ask_volume9.setter
    def ask_volume9(self, value):
        self.ask_volume[8] = value

    @property
    def ask_volume10(self):
        return self.ask_volume[9]

    @ask_volume10.setter
    def ask_volume10(self, value):
        self.ask_volume[9] = value

    @property
    def bid_price1(self):
        return self.bid_price[0]

    @bid_price1.setter
    def bid_price1(self, value):
        self.bid_price[0] = value

    @property
    def bid_price2(self):
        return self.bid_price[1]

    @bid_price2.setter
    def bid_price2(self, value):
        self.bid_price[1] = value

    @property
    def bid_price3(self):
        return self.bid_price[2]

    @bid_price3.setter
    def bid_price3(self, value):
        self.bid_price[2] = value

    @property
    def bid_price4(self):
        return self.bid_price[3]

    @bid_price4.setter
    def bid_price4(self, value):
        self.bid_price[3] = value

    @property
    def bid_price5(self):
        return self.bid_price[4]

    @bid_price5.setter
    def bid_price5(self, value):
        self.bid_price[4] = value

    @property
    def bid_price6(self):
        return self.bid_price[5]

    @bid_price6.setter
    def bid_price6(self, value):
        self.bid_price[5] = value

    @property
    def bid_price7(self):
        return self.bid_price[6]

    @bid_price7.setter
    def bid_price7(self, value):
        self.bid_price[6] = value

    @property
    def bid_price8(self):
        return self.bid_price[7]

    @bid_price8.setter
    def bid_price8(self, value):
        self.bid_price[7] = value

    @property
    def bid_price9(self):
        return self.bid_price[8]

    @bid_price9.setter
    def bid_price9(self, value):
        self.bid_price[8] = value

    @property
    def bid_price10(self):
        return self.bid_price[9]

    @bid_price10.setter
    def bid_price10(self, value):
        self.bid_price[9] = value

    @property
    def bid_volume1(self):
        return self.bid_volume[0]

    @bid_volume1.setter
    def bid_volume1(self, value):
        self.bid_volume[0] = value

    @property
    def bid_volume2(self):
        return self.bid_volume[1]

    @bid_volume2.setter
    def bid_volume2(self, value):
        self.bid_volume[1] = value

    @property
    def bid_volume3(self):
        return self.bid_volume[2]

    @bid_volume3.setter
    def bid_volume3(self, value):
        self.bid_volume[2] = value

    @property
    def bid_volume4(self):
        return self.bid_volume[3]

    @bid_volume4.setter
    def bid_volume4(self, value):
        self.bid_volume[3] = value

    @property
    def bid_volume5(self):
        return self.bid_volume[4]

    @bid_volume5.setter
    def bid_volume5(self, value):
        self.bid_volume[4] = value

    @property
    def bid_volume6(self):
        return self.bid_volume[5]

    @bid_volume6.setter
    def bid_volume6(self, value):
        self.bid_volume[5] = value

    @property
    def bid_volume7(self):
        return self.bid_volume[6]

    @bid_volume7.setter
    def bid_volume7(self, value):
        self.bid_volume[6] = value

    @property
    def bid_volume8(self):
        return self.bid_volume[7]

    @bid_volume8.setter
    def bid_volume8(self, value):
        self.bid_volume[7] = value

    @property
    def bid_volume9(self):
        return self.bid_volume[8]

    @bid_volume9.setter
    def bid_volume9(self, value):
        self.bid_volume[8] = value

    @property
    def bid_volume10(self):
        return self.bid_volume[9]

    @bid_volume10.setter
    def bid_volume10(self, value):
        self.bid_volume[9] = value

    def clone(self):
        quote = Quote()
        for data in self._askPrice:
            quote._askPrice.append(data)
        for data in self._askVolume:
            quote._askVolume.append(data)
        for data in self._bidPrice:
            quote._bidPrice.append(data)
        for data in self._bidVolume:
            quote._bidVolume.append(data)

    def to_string(self):
        raise Exception("该功能未实现")