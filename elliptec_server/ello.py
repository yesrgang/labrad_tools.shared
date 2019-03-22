import serial
import struct

class ELLO(object):
    def __init__(self, serial_port):
        ser = serial.Serial(serial_port)
        ser.timeout = 0.1
        self._ser = ser

    def home(self, address):
        self._ser.write('{}ho0'.format(address))
    
    def move_absolute(self, address, position_mm):
        position_str = struct.pack('>I', position_mm * 2048).encode('hex').upper()
        print '{}ma{}'.format(address, position_str)
        self._ser.write('{}ma{}'.format(address, position_str))
        result = self._ser.readline()
        print result

    def get_position(self, address):
        self._ser.write('{}gp')
        result = self._ser.readline()
        print result

