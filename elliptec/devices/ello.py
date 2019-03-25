import struct

from serial_server.proxy import SerialProxy

class ELLO(object):
    serial_port = None
    address = 0

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'serial' not in globals():
            global serial
            import serial
        ser = serial.Serial(self.serial_port)
        ser.timeout = 1
        self._ser = ser

    def home(self):
        self._ser.write('{}ho0'.format(self.address))
    
    @property
    def position(self):
        return self._get_position()

    @position.setter
    def position(self, position):
        self._move_absolute(position)
    
    def _move_absolute(self, position_mm):
        position_hex = struct.pack('>I', position_mm * 2048)
        position_str = position_hex.encode('hex').upper()
        self._ser.write('{}ma{}'.format(self.address, position_str))
        result = self._ser.readline()
        position_str = result.strip().split('PO')[1]
        position_hex = position_str.decode('hex')
        position = struct.unpack('>I', position_hex)[0]
        return float(position) / 2048

    def _get_position(self):
        self._ser.write('{}gp'.format(self.address))
        result = self._ser.readline()
        position_str = result.strip().split('PO')[1]
        position_hex = position_str.decode('hex')
        position = struct.unpack('>I', position_hex)[0]
        return float(position) / 2048


class ELLOProxy(ELLO):
    serial_servername = None

    def __init__(self, cxn=None, **kwargs):
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        global serial
        serial_server = cxn[self.serial_servername]
        serial = SerialProxy(serial_server)
        ELLO.__init__(self, **kwargs)
