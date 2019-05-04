class FrequencyOutOfBoundsError(Exception):
    pass

class AmplitudeOutOfBoundsError(Exception):
    pass

class DS345(object):
    _amplitude_range = (-36, 20)
    _amplitude_units = 'dB'
    _frequency_range = (1e-6, 30e6)
    _visa_address = None
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'visa' not in globals():
            global visa
            import visa
        rm = visa.ResourceManager()
        self._inst = rm.open_resource(self._visa_address)
    
    @property
    def state(self):
        return True
    
    @property
    def frequency(self):
        command = 'FREQ?'
        response = self._inst.query(command)
        return float(response)
    
    @frequency.setter
    def frequency(self, frequency):
        if frequency < min(self._frequency_range) or frequency > max(self._frequency_range):
            raise FrequencyOutOfBoundsError(frequency)
        command = 'FREQ {}'.format(frequency)
        self._inst.write(command)
    
    @property
    def amplitude(self):
        command = 'AMPL? {}'.format(self._amplitude_units)
        response = self._inst.query(command)
        return float(response[:-3])
    
    @amplitude.setter
    def amplitude(self, amplitude):
        command = 'AMPL {}{}'.format(amplitude, self.amplitude_units)
        self._inst.write(command)

class DS345Proxy(DS345):
    _visa_servername = None

    def __init__(self, cxn=None, **kwargs):
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        from visa_server2.proxy import VisaProxy
        global visa
        visa = VisaProxy(cxn[self._visa_servername])
        DS345.__init__(self, **kwargs)
