# A serial class emulator. Designed to be an abstract class
class FakeSerial:
    simple_commands = {}
    registered_commands = {}

    def __init__(self, port, baudrate=19200, timeout=1,
                 bytesize=8, parity='N', stopbits=1, xonxoff=0,
                 rtscts=0):
        self.name = port
        self.port = port
        self.timeout = timeout
        self.parity = parity
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.stopbits = stopbits
        self.xonxoff = xonxoff
        self.rtscts = rtscts
        self._isOpen = True
        self._receivedData = ""
        self._data = ""

    @classmethod
    def register_command(cls, name, type_conv):
        def inner(func):
            cls.registered_commands[name] = (func, type_conv)
            return func
        return inner

    def isOpen(self):
        return self._isOpen

    def open(self):
        self._isOpen = True

    def close(self):
        self._isOpen = False

    def write(self, string):
        self._receivedData += string
        self._process_received()

    def read(self, n=1):
        """
        reads n characters from data buffer
        """
        s = self._data[0:n]
        self._data = self._data[n:]
        return s

    def readline(self):
        try:
            returnIndex = self._data.index("\n")
        except ValueError:
            return ""
        else:
            s = self._data[0:returnIndex+1]
            self._data = self._data[returnIndex+1:]
            return s

    def __str__(self):
        template = "Serial<id=0xa81c10, open={}>(port='{}', baudrate={},"
        template += " bytesize={:d}, parity='{}', stopbits={:d}, xonxoff={:d}, rtscts={:d})"
        return template.format(
            str(self.isOpen()), self.port, self.baudrate,
            self.bytesize, self.parity, self.stopbits, self.xonxoff,
            self.rtscts
        )

    def _process_received(self):
        # if it's a simple command, send response
        if self._receivedData in self.simple_commands:
            cmd = self._receivedData
            self._receivedData = ""
            template = str(self.simple_commands[cmd])
            msg = template.format(**self.__dict__)
            self._data = msg + "\n"

        # for more complex commands, strip command from data
        # call function, append response
        for cmd in self.registered_commands:
            if self._receivedData.startswith(cmd):
                func, converter = self.registered_commands[cmd]

                arg = self._receivedData.strip(cmd)
                if len(arg) == 0:
                    result = func(self)
                else:
                    if converter is not None:
                        arg = converter(arg)
                    result = func(self, arg)

                result = str(result) + "\n" if result is not None else ""
                self._data = result
                self._receivedData = ""
