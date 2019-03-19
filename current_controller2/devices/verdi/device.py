from twisted.internet.reactor import callLater

from device_server.device import DefaultDevice
from current_controller.devices.verdi.helpers import seconds_til_start, cancel_delayed_calls
from serial_server.proxy import SerialProxy

class Verdi(DefaultDevice):
    serial_servername = None
    serial_address = None
    serial_timeout = 0.25
    serial_baudrate = 19200

    power_range = (0.0, 18.0)
    default_power = 18.0

    delayed_calls = []

    def initialize(self, config):
        super(Verdi, self).initialize(config)

        self.connect_to_labrad()
        self.serial_server = self.cxn[self.serial_servername]
        serial = SerialProxy(self.serial_server)

        ser = serial.Serial(self.serial_address)
        ser.timeout = self.serial_timeout
        ser.baudrate = self.serial_baudrate
        self.ser = ser

    def set_state(self, state):
        if state:
            commad = 'Laser: 1\r\n'
        else:
            commad = 'Laser: 0\r\n'
        self.ser.write(command)
        response = self.ser.readlines()

    def get_state(self):
        command = 'Print Laser\r\n'
        self.ser.write(command)
        response = self.ser.readlines()
        state = bool(response[0])
        return state

    def set_shutter_state(self, shutter_state):
        if shutter_state:
            commad = 'Shutter: 1\r\n'
        else:
            commad = 'Shutter: 0\r\n'
        self.ser.write(command)
        response = self.ser.readlines()

    def get_shutter_state(self):
        command = 'Print Sutter\r\n'
        self.ser.write(command)
        response = self.ser.readlines()
        shutter_state = bool(response[0])
        return shutter_state

    def set_power(self, power):
        command = 'Light: {}'.format(power)
        self.ser.write(command)
        response = self.ser.readlines()

    def get_power(self):
        command = 'Print Light'
        self.ser.write(command)
        response = self.ser.readlines()
        return float(response[0])

    def set_current(self, current):
        # could raise Exception here
        pass

    def get_current(self):
        command = 'Print Current'
        self.ser.write(command)
        response = self.ser.readlines()
        return float(response[0])

    def warmup(self, kw):
        self.set_power(self.default_power)
        self.set_state(True)
        self.set_shutter_state(True)

    def shutdown(self):
        self.set_shutter_state(False)
        self.set_state(False)
        self.set_power(self.warmup_power)
