import gzip


class MAFWriter:
    def __init__(self, path, compression=None):
        self.path = path
        self.compression_extensions = {
            "gzip": ".gz"
        }
        self._parsers = {
            "gzip": gzip.open,
            "native": open
        }
        self.compression = compression
        if self.compression:
            self._parser = self._parsers[compression]
            self.path += self.compression_extensions[compression]
        else:
            self._parser = self._parsers["native"]

    def write(self, data, append=False):
        mode = "rb"
        if append:
            mode= "ab"
        
        with self._parser(self.path, mode) as file:
            raw_data = ""
            for row in data:
                raw_data = raw_data + \
                    "".join([val + "\t" for val in row]).rstrip("\t") + "\n"

            file.write(raw_data.encode())