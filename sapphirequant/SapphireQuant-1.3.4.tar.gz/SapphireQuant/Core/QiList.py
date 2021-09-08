class QiList(list):
    """
    QiList
    """
    @property
    def length(self):
        """
        返回序列的个数
        :return:
        """
        return len(self)

    @property
    def first(self):
        """
        序列的第一个元素
        :return:
        """
        if len(self) > 0:
            return self[0]
        else:
            return None

    @property
    def last(self):
        """
        序列的最后一个元素
        :return:
        """
        if len(self) > 0:
            return self[-1]
        else:
            return None

    @last.setter
    def last(self, value):
        if len(self) > 0:
            self[-1] = value

    @property
    def last_index(self):
        """
        返回当前序列的最后一个index
        :return:
        """
        return self.length - 1

    def ago(self, n):
        """
        返回当前序列从最后一个往前回溯指定个数的一个元素
        example:
        list = ['a', 'b', 'c', 'd']
        ago(0) = 'd'
        ago(1) = 'c'
        :param n:
        :return:
        """
        if n <= 0:
            return self.last
        if n >= (self.length - 1):
            return self.first
        return self[self.length - 1 - n]

    def ago_sub(self, n, m):
        """
        返回区间，包含头尾
        example:
        list = ['a', 'b', 'c', 'd']
        ago(0， 1) = ['c', 'd']
        ago(0, 2) = ['b', 'c', 'd']
        :param n:
        :param m:
        :return:
        """
        qi_list = QiList()
        num = max(n, m)
        num2 = min(n, m)
        num = max(0, num)
        num = min(self.length - 1, num)
        num2 = max(0, num2)
        num2 = min(self.length - 1, num2)
        for i in range(self.length - 1 - num, self.length - num2):
            qi_list.append(self[i])
        return qi_list

#
# data = QiList()
# data.append('a')
# data.append('b')
# data.append('c')
# data.append('d')
# data.append('e')
# data.append('f')
# data.append('g')
# print(data.first)
# print(data.last)
# print(data.last_index)
# print(data.ago(1))
# print(data.ago_sub(0, 1))
