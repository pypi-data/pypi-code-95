class Response:
    result: dict = {}
    failed: list = []
    start_time: float = 0.0
    end_time: float = 0.0

    @property
    def run_time(self):
        return self.end_time - self.start_time
