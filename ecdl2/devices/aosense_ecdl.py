class AOSenseECDL(object):
    _serial_address = None
    _serial_timeout = 0.05
    _serial_baudrate = 115200
    
    _diode_current_range = (10.0, 200.0) # [mA]
    _piezo_voltage_range = (0.0, 125.0) # [V]
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'serial' not in globals():
            global serial
            import serial
        ser = serial.Serial(self._serial_address)
        ser.timeout = self._serial_timeout
        ser.baudrate = self._serial_baudrate
        self._ser = ser

    @property
    def state(self):
        command = 'LASER\r\n'
        self._ser.write(command)
        response = self._ser.readlines()
        if 'OFF' not in response[0]:
            return True
        else:
            return False
    
    @state.setter
    def state(self, state):
        if state:
            command = 'LASER ON\r\n'
        else:
            command = 'LASER OFF\r\n'
        self._ser.write(command)
        response = self._ser.readlines()
    
    @property
    def diode_current(self):
        command = 'ILA\r\n'
        self._ser.write(command)
        response = self._ser.readlines()
        return float(response[0].split('=')[-1])

    @diode_current.setter
    def diode_current(self, diode_current):
        min_current = min(self._diode_current_range)
        max_current = max(self._diode_current_range)
        current = sorted([min_current, diode_current, max_current])[1]
        command = 'ILA {}\r\n'.format(round(current, 5))
        self._ser.write(command)
        response = self._ser.readlines()
    
    @property
    def piezo_voltage(self):
        command = 'UPZ\r\n'
        self._ser.write(command)
        response = self._ser.readlines()
        return float(response[0].split('=')[-1])
   
    @piezo_voltage.setter
    def piezo_voltage(self, piezo_voltage):
        min_voltage = self._piezo_voltage_range[0]
        max_voltage = self._piezo_voltage_range[1]
        voltage = sorted([min_voltage, piezo_voltage, max_voltage])[1]
        command = 'UPZ {}\r\n'.format(voltage)
        self._ser.write(command)
        response = self._ser.readlines()

class AOSenseECDLProxy(AOSenseECDL):
    _serial_servername = None

    def __init__(self, cxn=None, **kwargs):
        from serial_server.proxy import SerialProxy
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        global serial
        serial_server = cxn[self._serial_servername]
        serial = SerialProxy(serial_server)
        AOSenseECDL.__init__(self, **kwargs)
