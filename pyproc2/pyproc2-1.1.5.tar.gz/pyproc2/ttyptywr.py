import serial
class TTY:
    def __init__(self,file):
        self.ser = serial.Serial()
        self.ser.port = file
        self.ser.open()
        self.ser.flushInput()
        self.ser.flushOutput()
        self.ser.baudrate = 9600
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.timeout = 0 # Non-Block reading
        self.ser.xonxoff = False # Disable Software Flow Control
        self.ser.rtscts = False # Disable (RTS/CTS) flow Control
        self.ser.dsrdtr = False # Disable (DSR/DTR) flow Control
        self.ser.writeTimeout = 2
         
    def cmd(self, cmd_str):
        self.ser.write((cmd_str + "\n").encode())
        return self.ser.readline().decode()
    def close(self):
        self.ser.close()
