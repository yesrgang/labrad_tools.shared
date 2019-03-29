from device_server.device import DefaultDevice
from visa_server.proxy import VisaProxy

class DS345(DefaultDevice):
    visa_servername = None
    visa_address = None
    
    state = None

    amplitude = None
    amplitude_range = (-36, 20)
    amplitude_units = 'dB'

    frequency = None
    frequency_range = (1e-6, 30e6)

    update_parameters = ['state', 'frequency', 'amplitude']

    def initialize(self, config):
        super(DS345, self).initialize(config)
        self.connect_to_labrad()
        
        self.visa_server = self.cxn[self.visa_servername]
        visa = VisaProxy(self.visa_server)
        rm = visa.ResourceManager()
        rm.open_resource(self.visa_address)
        self.visa = visa
        self.rm = rm

        self.do_update_parameters()

    def do_update_parameters(self):
        self.state = self.get_state()
        self.frequency = self.get_frequency()
        self.amplitude = self.get_amplitude()

    def get_state(self):
        return True
    
    def set_state(self):
        pass
    
    def set_frequency(self, frequency):
        frequency = sorted([min(self.frequency_range), 
            max(self.frequency_range), frequency])[1]
        command = 'FREQ {}'.format(frequency)
        self.rm.write(command)

    def get_frequency(self):
        ans = self.rm.query('FREQ?')
        return float(ans)

    def set_amplitude(self, amplitude):
        amplitude = sorted([min(self.amplitude_range), 
            max(self.amplitude_range), amplitude])[1]
        command = 'AMPL {}{}'.format(amplitude, self.amplitude_units)
        self.rm.write(command)

    def get_amplitude(self):
        ans = self.rm.query('AMPL?')
        return float(ans[:-2])

