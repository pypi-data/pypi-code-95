import datetime
import uuid


class Entity:
    """
    父类
    """
    def __init__(self):
        self.account_id = ''
        self.guid = uuid.uuid1()
        self.product_code = -1
        self.strategy_id = -1
        self.param_id = ''
        self.trading_date = datetime.datetime.today()
        self.update_time = datetime.datetime.today()