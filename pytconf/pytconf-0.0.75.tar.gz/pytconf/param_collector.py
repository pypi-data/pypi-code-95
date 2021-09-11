class ParamCollector:
    def __init__(self):
        self.data = []

    def add_data(self, item):
        self.data.append(item)

    def clear(self):
        self.data = []

    def get_item(self, i):
        return self.data[i]

    def yield_items(self):
        for item in self.data:
            yield item


the_collector: ParamCollector = ParamCollector()
