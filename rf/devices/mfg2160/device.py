from device_server.device import DefaultDevice
from serial_server.proxy import SerialProxy

class MFG2160(DefaultDevice):
    serial_servername = None
    serial_address = None
    serial_timeout = 0.2 # [s]
    
    source = 3

    state = None

    amplitude = None
    amplitude_range = None

    frequency = None
    frequency_range = None

    update_parameters = ['state', 'frequency', 'amplitude']

    def initialize(self, config):
        super(MFG2160, self).initialize(config)

        self.connect_to_labrad()
        self.serial_server = self.cxn[self.serial_servername]

        serial = SerialProxy(self.serial_server)
        ser = serial.Serial(self.serial_address)
        ser.timeout = self.serial_timeout
        self.ser = ser

    def do_update_parameters(self):
        self.state = self.get_state()
        self.frequency = self.get_frequency()
        self.amplitude = self.get_amplitude()

    def get_state(self):
        return True
    
    def set_state(self):
        pass
    
    def set_frequency(self, frequency):
        command = 'SOUR3RF:FREQ {}\r\n'.format(frequency)
        self.ser.write(command)

    def get_frequency(self):
        command = 'SOUR3RF:FREQ?\r\n'
        self.ser.writeline(command)
        response = self.ser.readlines()
        return float(response[0])

    def set_amplitude(self, amplitude):
        command = 'SOUR3RF:AMP {}\r\n'.format(amplitude)
        self.ser.write(command)

    def get_amplitude(self):
        command = 'SOUR3RF:AMP?\r\n'
        self.ser.write(command)
        response = self.ser.readlines()
        return float(response[0])

