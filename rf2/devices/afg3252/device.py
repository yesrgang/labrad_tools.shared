from device_server.device import DefaultDevice

class AFG3252(DefaultDevice):
    visa_server_name = None
    visa_address = None

    source = None
    
    frequency = None
    frequency_range = None

    update_parameters = ['frequency']

    def initialize(self, config):
        super(AFG3252, self).initialize(config)
        self.connect_to_labrad()
        self.visa_server = self.cxn[self.visa_server_name]
        self.visa_server.open_interface(self.visa_address)

    def set_frequency(self, frequency):
        command = 'SOUR{}:FREQ {}'.format(self.source, frequency)
        self.visa_server.write(self.visa_address, command)

    def get_frequency(self):
        command = 'SOUR{}:FREQ?'.format(self.source)
        response = self.visa_server.query(self.visa_address, command)
        return float(response)

