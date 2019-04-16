class E44xx(object):
    _visa_address = None
    
    amplitude_range = None
    amplitude_units = None

    frequency_range = None
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'visa' not in globals():
            global visa
            import visa
        rm = visa.ResourceManager()
        self._inst = rm.open_resource(self._visa_address)

    def set_state(self, state):
        command = 'OUTP:STAT {}'.format(int(bool(state)))
        self.rm.write(command)

    def get_state(self):
        ans = self.rm.query('OUTP:STAT?')
        return bool(int(ans))
    
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
        frequency = sorted([min(self._frequency_range), 
            max(self._frequency_range), frequency])[1]
        command = 'FREQ:CW {} Hz'.format(frequency)
        self._inst.write(command)

    @property
    def amplitude(self):
        command = 'POW:AMPL?'
        ans = self._inst.query(command)
        return float(ans)
    
    @amplitude.setter
    def amplitude(self, amplitude):
        amplitude = sorted([min(self._amplitude_range), 
            max(self._amplitude_range), amplitude])[1]
        command = 'POW:AMPL {} {}'.format(amplitude, self._amplitude_units)
        self._inst.write(command)
        
class E44xxProxy(E44xx):
    _visa_servername = None

    def __init__(self, cxn=None, **kwargs):
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        global visa
        from visa_server2.proxy import VisaProxy
        visa_server = cxn[self._visa_servername]
        visa = VisaProxy(visa_server)
        E44xx.__init__(self, **kwargs)
