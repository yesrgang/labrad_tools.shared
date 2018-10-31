import vxi11

from device_server.device import DefaultDevice

class AG53220A(DefaultDevice):
    vxi11_address = None
    
    channel = None

    def initialize(self, config):
        super(AG53220A, self).initialize(config)
        self.vxi11 = vxi11.Instrument(self.vxi11_address)
        print self.vxi11_address

    def get_frequency(self):
        command = 'MEAS:FREQ? DEF, DEF, (@{})'.format(self.channel)
        response = self.vxi11.ask(command)
        return float(response)
