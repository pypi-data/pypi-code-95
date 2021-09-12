class EndpointVersionData:

    def __init__(self, data):
        self.compute = data.get("compute_name")
        self.image = data.get("image_name")
        self.file = data.get("file_name")
