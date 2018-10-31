from device_server.device import DefaultDevice
from serial_server.proxy import SerialProxy

class SilverPack17(DefaultDevice):
    serial_servername = None
    serial_address = None
    serial_timeout = 0.5

    def initialize(self, config):
        super(SilverPack17, self).initialize(config)
        
        self.connect_to_labrad()
        self.serial_server = self.cxn[self.serial_servername]
        serial = SerialProxy(self.serial_server)

        ser = serial.Serial(self.serial_address)
        ser.timeout = self.serial_timeout
        self.ser = ser

        # set current
        command = '/1m30h10R\r'
        self.ser.write(command)
        response = self.ser.readline()
        self.serial_server.write(self.serial_address, )
        response = self.serial_server.readline(self.serial_address)

        # set velocity and acceleration
        command = '/1V1000L500R\r'
        self.ser.write(command)
        response = self.ser.readline()

        # set step resolution
        command = '/1j256o1500R\r'
        self.ser.write(command)
        response = self.ser.readline()
    
    def move_absolute(self, position):
        command = '/1A{}R\r'.format(position)
        self.ser.write(command)
        response = self.ser.readline()
        self.position = position

    def toggle_absolute(self,position1, position2):
        command = '/1gH04A{}H14A{}G0R\r'.format(position1, position2)
        response = self.serial_server.readline(self.serial_address)
#        command = '/1s0gH04A{}H14A{}G0R\r'.format(position1, position2)
#        yield self.serial_server.write(command)
#        response = yield self.serial_server.read_line()
#        yield self.serial_server.write('/1e0R\r')
#        response = yield self.serial_server.read_line()
