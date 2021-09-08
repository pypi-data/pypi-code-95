
class FutureProduct:
    """
    期货产品
    """
    def __init__(self, product_id="", product_name="", exchange_id=""):
        self._product_id = product_id
        self._product_name = product_name
        self._exchange_id = exchange_id
        self._futures = []
        self.future_map = {}
        self._all_slice = []

    @property
    def product_id(self):
        """
        产品id
        :return:
        """
        return self._product_id

    @product_id.setter
    def product_id(self, value):
        self._product_id = value

    @property
    def product_name(self):
        """
        产品名称
        :return:
        """
        return self._product_name

    @product_name.setter
    def product_name(self, value):
        self._product_name = value

    @property
    def exchange_id(self):
        """
        交易市场id
        :return:
        """
        return self._exchange_id

    @exchange_id.setter
    def exchange_id(self, value):
        self._exchange_id = value

    @property
    def futures(self):
        """
        期货合约列表
        :return:
        """
        return self._futures

    @futures.setter
    def futures(self, value):
        self._futures = value

    @property
    def all_slice(self):
        """

        :return:
        """
        return self._all_slice

    def init(self, product):
        """
        构造函数
        :param product:
        """
        self._product_id = product.product_id
        self._product_name = product.product_name
        self._exchange_id = product.exchange_id
        self._all_slice.append(product.all_slice)

    def to_string(self):
        """
        转成string
        :return:
        """
        string_builder = self._product_id
        string_builder += ("[" + self._product_name + "]")
        string_builder += "交易所=" + self._exchange_id

        return string_builder
