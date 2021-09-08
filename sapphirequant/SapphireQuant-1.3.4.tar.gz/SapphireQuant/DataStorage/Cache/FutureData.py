

class FutureData:
    """
    期货清算数据
    """
    def __init__(self):
        self.asset = None
        self.positions = []
        self.position_details = []
        self.orders = []
        self.trades = []
        self.next_asset = None
        self.next_positions = []
        self.next_position_details = []