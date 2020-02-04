import struct

from serial_server.proxy import SerialProxy

class ELL6(object):
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
        self._ser.write('{}gp'.format(self.address))
        result = self._ser.readline()
        position_str = result.strip().split('PO')[1]
        position_hex = position_str.decode('hex')
        position = struct.unpack('>I', position_hex)[0]
        return int(bool(position))

    @position.setter
    def position(self, position):
        if position:
            self._ser.write('{}fw'.format(self.address))
        else:
            self._ser.write('{}bw'.format(self.address))
        result = self._ser.readline()
        position_str = result.strip().split('PO')[1]
        position_hex = position_str.decode('hex')
        position = struct.unpack('>I', position_hex)[0]
        return int(bool(position))


class ELL6Proxy(ELL6):
    serial_servername = None

    def __init__(self, cxn=None, **kwargs):
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        global serial
        serial_server = cxn[self.serial_servername]
        serial = SerialProxy(serial_server)
        ELL6.__init__(self, **kwargs)
