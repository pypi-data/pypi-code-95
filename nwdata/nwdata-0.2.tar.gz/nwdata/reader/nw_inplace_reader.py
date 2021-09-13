from .reader import Reader

class NWInplaceReader(Reader):
    def __init__(self, data, labels):
        self.data = data
        self.labels = labels
        assert len(self.data) == len(self.labels)
        super().__init__(
            dataBuckets = {"data" : ["data"], "labels" : ["labels"]},
            dimGetter = {
                "data" : lambda d, i : d["data"][i],
                "labels" : lambda d, i : d["labels"][i]
            },
            dimTransform = {}
        )
    
    def getDataset(self):
        return {"data" : self.data, "labels" : self.labels}

    def __len__(self):
        return len(self.data)