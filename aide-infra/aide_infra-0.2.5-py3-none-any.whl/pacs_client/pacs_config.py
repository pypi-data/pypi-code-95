class PacsConfiguration:
    def __init__(self, ae_title, host, port, dimse_timeout=30):
        self.ae_title = ae_title
        self.host = host
        self.port = port
        self.dimse_timeout = dimse_timeout
