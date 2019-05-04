class KJL375(object):
    _serial_port = None
    _serial_timeout = 0.05
    _serial_baudrate = 19200

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'serial' not in globals():
            global serial
            import serial
        self._ser = serial.Serial(self._serial_port)
        self._ser.timeout = self._serial_timeout
        self._ser.baudrate = self._serial_baudrate
    
    @property
    def pressure(self):
        self._ser.write('#01RD\r')
        response = self._ser.readline()
        return float(response[4:-1])

class KJL375Proxy(KJL375):
    _serial_servername = None

    def __init__(self, cxn=None, **kwargs):
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        from serial_server.proxy import SerialProxy
        global serial
        serial = SerialProxy(cxn[self._serial_servername])
        KJL375.__init__(self, **kwargs)


    
