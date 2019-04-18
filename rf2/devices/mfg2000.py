class FrequencyOutOfBoundsError(Exception):
    pass

class AmplitudeOutOfBoundsError(Exception):
    pass

class MFG2000(object):
    _amplitude_range = (-float('inf'), float('inf'))
    _frequency_range = (0, float('inf'))
    _serial_port = None
    _serial_timeout = 0.2
    _source = 3
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'serial' not in globals():
            global serial
            import serial
        self._ser = serial.Serial(self._serial_port)
        self._ser.timeout = self._serial_timeout
    
    @property
    def state(self):
        return True
    
    @property
    def frequency(self):
        command = 'SOUR{}RF:FREQ?\r\n'.format(self._source)
        self._ser.writeline(command)
        response = self._ser.readlines()
        return float(response[0])
    
    @frequency.setter
    def frequency(self, frequency):
        if frequency < min(self._frequency_range) or frequency > max(self._frequency_range):
            raise FrequencyOutOfBoundsError(frequency)
        command = 'SOUR{}RF:FREQ {}\r\n'.format(self._source, frequency)
        self._ser.write(command)

    @property
    def amplitude(self):
        command = 'SOUR{}RF:AMP?\r\n'.format(self._source)
        self._ser.write(command)
        response = self._ser.readlines()
        return float(response[0])
    
    @amplitude.setter
    def amplitude(self, amplitude):
        if amplitude < min(self._amplitude_range) or amplitude > max(self._amplitude_range):
            raise AmplitudeOutOfBoundsError(amplitude)
        command = 'SOUR{}RF:AMP {}\r\n'.format(self._source, amplitude)
        self._ser.write(command)

class MFG2000Proxy(MFG2000):
    _serial_servername = None

    def __init__(self, cxn=None, **kwargs):
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        from serial_server.proxy import SerialProxy
        global serial
        serial = SerialProxy(cxn[self._serial_servername])
        MFG2000.__init__(self, **kwargs)
