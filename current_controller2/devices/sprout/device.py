from time import sleep

from device_server.device import DefaultDevice
from serial_server.proxy import SerialProxy

class Sprout(DefaultDevice):
    serial_servername = None
    serial_address = None
    serial_timeout = 0.25
    serial_baudrate = 19200

    power_range = (0.0, 18.0)
    power_default = 18.0

    def initialize(self, config):
        super(Sprout, self).initialize(config)
        self.connect_to_labrad()
        self.serial_server = self.cxn[self.serial_servername]

        serial = SerialProxy(self.serial_server)
        ser = serial.Serial(self.serial_address)
        ser.timeout = self.serial_timeout
        ser.baudrate = self.serial_baudrate
        self.ser = ser

#        self.serial_server.reopen_interface(self.serial_address)
#        self.serial_server.timeout(self.serial_address, self.serial_timeout)
#        self.serial_server.baudrate(self.serial_address, self.serial_baudrate)
    
    def set_state(self, state):
        if state:
            command = 'OPMODE=ON\r\n'
        else:
            command = 'OPMODE=OFF\r\n'
        self.ser.write(command)
        response = self.ser.readlines()
#        self.serial_server.write(self.serial_address, command)
#        response = self.serial_server.readlines(self.serial_address)

    def get_state(self):
        command = 'OPMODE?\r\n'
        self.ser.write(command)
        response = self.ser.readlines()
#        self.serial_server.write(self.serial_address, command)
#        response = self.serial_server.readlines(self.serial_address)
        if response == 'OPMODE=ON':
            state = True
        else:
            state = False
        return state

    def set_power(self, power):
        command = 'Power set={}\r\n'.format(power)
        self.ser.write(command)
        response = self.ser.readlines()
#        self.serial_server.write(self.serial_address, command)
#        response = self.serial_server.readlines(self.serial_address)

    def get_power(self):
        command = 'Power?\r\n'
        self.ser.write(command)
        response = self.ser.readlines()
#        self.serial_server.write(self.serial_address, command)
#        response = self.serial_server.readlines(self.serial_address)
        return float(response[0][6:])

    def warmup(self, kw):
        self.set_power(self.power_default)
        self.set_state(True)
        return True

    def shutdown(self, kw):
        self.set_power(0)
        self.set_state(False)
        return True
