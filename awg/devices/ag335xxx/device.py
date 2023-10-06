import vxi11

from device_server.device import DefaultDevice

class AG335xxx(DefaultDevice):
    vxi11_address = None
    source = None

    waveforms = None

    update_parameters = []

    def initialize(self, config):
        super(AG335xxx, self).initialize(config)
        self.vxi11 = vxi11.Instrument(self.vxi11_address)
        command = 'SOUR{}:DATA:VOL:CLE'.format(self.source)
        self.vxi11.write(command)
        for waveform in self.waveforms:
            command = 'MMEM:LOAD:DATA{} "{}"'.format(self.source, waveform)
            self.vxi11.write(command)
            command = 'SOUR{}:FUNC:ARB "{}"'.format(self.source, waveform)
            self.vxi11.write(command)

    def set_waveform(self, waveform):
        if waveform not in self.waveforms:
            message = 'waveform "{}" not configured'.format(waveform)
            raise Exception(message)
        command = 'SOUR{}:FUNC:ARB "{}"'.format(self.source, waveform)
        self.vxi11.write(command)

    def get_waveform(self):
        command = 'SOUR{}:FUNC:ARB?'.format(self.source)
        ans = self.vxi11.ask(command)
        return ans
    
    def set_amplitude(self, amplitude):
        command = 'SOUR{}:VOLT {}'.format(self.source, amplitude)
        self.vxi11.write(command)
    
    def get_amplitude(self):
        command = 'SOUR{}:VOLT?'.format(self.source)
        ans = self.vxi11.ask(command)
        return float(ans)
