from device_server.device import DefaultDevice
from serial_server.proxy import SerialProxy

class PSH6018(DefaultDevice):
    serial_servername = None
    serial_address = None
    serial_timeout = .5

    current_range = (0.0, 10.0)
    voltage_range = (0.0, 5.0)
    update_parameters = [
        'state', 
        'current', 
        'voltage', 
        'current_limit', 
        'voltage_limit',
        ]

    def initialize(self, config):
        super(PSH6018, self).initialize(config)
        self.connect_to_labrad()
        self.serial_server = self.cxn[self.serial_servername]
       
        serial = SerialProxy(self.serial_server)
        ser = serial.Serial(self.serial_address)
        ser.timeout = self.serial_timeout
        ser.readlines()
        self.ser = ser
       
        self.get_parameters()
    
    def get_parameters(self):
        self.get_state()
        self.get_current()
        self.get_voltage()
        self.get_current_limit()
        self.get_voltage_limit()

    def get_current(self):
        command = 'CHAN:MEAS:CURR?\r\n'
        self.ser.write(command)
        response = self.ser.readline()
        current = float(response.strip())
        self.current = current
        return current
    
    def get_current_limit(self):
        command = 'CHAN:CURR?\r\n'
        self.ser.write(command)
        response = self.ser.readline()
        current_limit = float(response.strip())
        self.current_limit = current_limit
        return current_limit

    def set_current_limit(self, current):
        min_current = self.current_range[0]
        max_current = self.current_range[1]
        current = sorted([min_current, current, max_current])[1]
        command = 'CHAN:CURR {}\r\n'.format(current)
        self.ser.write(command)
        
        self.get_current()
        self.get_voltage()
    
    def get_voltage(self):
        command = 'CHAN:MEAS:VOLT?\r\n'
        self.ser.write(command)
        response = self.ser.readline()
        voltage = float(response.strip())
        self.voltage = voltage
        return voltage
    
    def get_voltage_limit(self):
        command = 'CHAN:VOLT?\r\n'
        self.ser.write(command)
        response = self.ser.readline()
        voltage_limit = float(response.strip())
        self.voltage_limit = voltage_limit
        return voltage_limit

    def set_voltage_limit(self, voltage):
        min_voltage = self.voltage_range[0]
        max_voltage = self.voltage_range[1]
        voltage = sorted([min_voltage, voltage, max_voltage])[1]
        command = 'CHAN:VOLT {}\r\n'.format(voltage)
        self.ser.write(command)
        
        self.get_current()
        self.get_voltage()

    def get_state(self):
        command = 'OUTP:STAT?\r\n'
        self.ser.write(command)
        response = self.ser.readline()
        state = bool(int(response.strip()))
        self.state = state
        return state
    
    def set_state(self, state):
        if state:
            command = 'OUTP:STAT 1\r\n'
        else:
            command = 'OUTP:STAT 0\r\n'
        self.ser.write(command)
        self.get_state()
