class Counter:
    def __init__(self,count):
        self.counter = count

    def get_count(self):
        return self.counter

    def set_count(self, count):
        self.counter = count

    def increment(self):
        self.counter += 1
        return self.counter

    count = property(get_count, set_count)