from pkgutil import extend_path
import serial
import struct

from serial_server.proxy import SerialProxy

__path__ = extend_path(__path__, __name__)

class ELLO(object):
    serial_port = None
    address = 0

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        ser = serial.Serial(self.serial_port)
        ser.timeout = 1
        self._ser = ser

    def home(self):
        self._ser.write('{}ho0'.format(self.address))
    
    def move_absolute(self, position_mm):
        position_hex = struct.pack('>I', position_mm * 2048)
        position_str = position_hex.encode('hex').upper()
        self._ser.write('{}ma{}'.format(self.address, position_str))
        result = self._ser.readline()
        position_str = result.strip().split('PO')[1]
        position_hex = position_str.decode('hex')
        position = struct.unpack('>I', position_hex)[0]
        return float(position) / 2048

    def get_position(self):
        self._ser.write('{}gp'.format(self.address))
        result = self._ser.readline()
        position_str = result.strip().split('PO')[1]
        position_hex = position_str.decode('hex')
        position = struct.unpack('>I', position_hex)[0]
        return float(position) / 2048


class ELLOProxy(ELLO):
    def __init__(self, serial_server, **kwargs):
        global serial
        serial = SerialProxy(serial_server)
        ELLO.__init__(self, **kwargs)
