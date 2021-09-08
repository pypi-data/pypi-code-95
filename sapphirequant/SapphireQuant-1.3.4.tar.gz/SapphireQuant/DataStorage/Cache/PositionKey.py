class PositionKey:
    """
    持仓唯一索引
    """
    def __init__(self, product_code, strategy_id, instrument_id, direction):
        self.product_code = product_code
        self.strategy_id = strategy_id
        self.instrument_id = instrument_id
        self.direction = direction

    def equals(self, obj):
        """

        :param obj:
        :return:
        """
        if not isinstance(obj, PositionKey):
            return False

        return (self.product_code == obj.product_code) & (self.strategy_id == obj.strategy_id) & (self.instrument_id == obj.instrument_id) & (
                self.direction == obj.direction)

    def get_hash_code(self):
        """

        :return:
        """
        return '{0}_{1}_{2}_{3}'.format(self.product_code, self.strategy_id, self.instrument_id, self.direction)

    def to_string(self):
        """

        :return:
        """
        return '{0}_{1}_{2}_{3}'.format(self.product_code, self.strategy_id, self.instrument_id, self.direction)