class MockRBMQConnectionManager:
    def __init__(self, mocked_channel):
        self.mocked_channel = mocked_channel

    def get_channel(self):
        return self.mocked_channel

    def close(self):
        pass

    def __enter__(self):
        return self.mocked_channel

    def __exit__(self, tp, vl, tb):
        self.mocked_channel.close()
