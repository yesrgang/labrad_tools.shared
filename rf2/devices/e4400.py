class FrequencyOutOfBoundsError(Exception):
    pass

class AmplitudeOutOfBoundsError(Exception):
    pass

class E4400(object):
    _amplitude_range = (-float('inf'), float('inf'))
    _amplitude_units = None
    _frequency_range = (0, float('inf'))
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
        command = 'OUTP:STAT?'
        ans = self._inst.query(command)
        return bool(int(ans))
    
    @state.setter
    def state(self, state):
        command = 'OUTP:STAT {}'.format(int(bool(state)))
        self._inst.write(command)
    
    @property
    def frequency(self):
        command = 'FREQ:CW?'
        ans = self._inst.query(command)
        return float(ans)
    
    @frequency.setter
    def frequency(self, frequency):
        if frequency < min(self._frequency_range) or frequency > max(self._frequency_range):
            raise FrequencyOutOfBoundsError(frequency)
        command = 'FREQ:CW {} Hz'.format(frequency)
        self._inst.write(command)

    @property
    def amplitude(self):
        command = 'POW:AMPL?'
        ans = self._inst.query(command)
        return float(ans)
    
    @amplitude.setter
    def amplitude(self, amplitude):
        if amplitude < min(self._amplitude_range) or amplitude > max(self._amplitude_range):
            raise AmplitudeOutOfBoundsError(amplitude)
        command = 'POW:AMPL {} {}'.format(amplitude, self._amplitude_units)
        self._inst.write(command)

class E4400Proxy(E4400):
    _visa_servername = None

    def __init__(self, cxn=None, **kwargs):
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        from visa_server2.proxy import VisaProxy
        global visa
        visa = VisaProxy(cxn[self._visa_servername])
        E4400.__init__(self, **kwargs)
