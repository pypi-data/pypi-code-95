class TwoReversedLister:
    def __init__(self, list):
        self.reversed_list_len = len(list) // 2
        self.reversed_list_len_1 = list[0 : self.reversed_list_len]
        self.list1 = list[self.reversed_list_len : len(list) + 1]
        self.list = self.reversed_list_len_1 + self.list1

    def __repr__(self):
        return str(self.list)
