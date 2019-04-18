class FrequencyOutOfBoundsError(Exception):
    pass

class AmplitudeOutOfBoundsError(Exception):
    pass

class AFG3xxx(object):
    _amplitude_range = None
    _amplitude_units = None
    _frequency_range = None
    _source = None
    _visa_address = None

    def __init__(self, **kwargs):
        try:
            visa = kwargs.pop('visa')
        except KeyError:
            import visa
        for key, value in kwargs.items():
            setattr(self, key, value)
        rm = visa.ResourceManager()
        self._inst = rm.open_resource(self._visa_address)

    @property
    def state(self):
        command = 'OUTP{}?'.format(self.source)
        ans = self._inst.query(command)
        if ans == 'ON':
            state = True
        else:
            state = False
        return state
    
    @state.setter
    def state(self, state):
        command = 'OUTP{}:STAT {}'.format(self.source, int(bool(state)))
        self._inst.write(command)

    @property
    def frequency(self):
        command = 'SOUR{}:FREQ?'.format(self.source)
        ans = self._inst.query(command)
        return float(ans)
    
    @frequency.setter
    def frequency(self, frequency):
        if frequency < min(self._frequency_range) or frequency > max(self._frequency_range):
            raise FrequencyOutOfBoundsError(frequency)
        command = 'SOUR{}:FREQ {}'.format(self.source, frequency)
        self._inst.write(command)
    
    @property
    def start_frequency(self):
        command = 'SOUR{}:FREQ:STAR?'.format(self.source)
        ans = self._inst.query(command)
        return float(ans)
    
    @start_frequency.setter
    def start_frequency(self, frequency):
        if frequency < min(self._frequency_range) or frequency > max(self._frequency_range):
            raise FrequencyOutOfBoundsError(frequency)
        command = 'SOUR{}:FREQ:STAR {}'.format(self.source, frequency)
        self._inst.write(command)
    
    @property
    def stop_frequency(self):
        command = 'SOUR{}:FREQ:STOP?'.format(self.source)
        ans = self._inst.query(command)
        return float(ans)
    
    @stop_frequency.setter
    def stop_frequency(self, frequency):
        if frequency < min(self._frequency_range) or frequency > max(self._frequency_range):
            raise FrequencyOutOfBoundsError(frequency)
        command = 'SOUR{}:FREQ:STOP {}'.format(self.source, frequency)
        self._inst.write(command)
    
    @property
    def amplitude(self):
        command = 'SOUR{}:VOLT?'.format(self.source)
        ans = self._inst.query(command)
        return float(ans)
    
    @amplitude.setter
    def amplitude(self, amplitude):
        if amplitude < min(self._amplitude_range) or amplitude > max(self._amplitude_range):
            raise AmplitudeOutOfBoundsError(amplitude)
        command = 'SOUR{}:VOLT {}'.format(self.source, amplitude)
        self._inst.write(command)
        
    @property
    def offset(self):
        command = 'SOUR{}:VOLT:OFFS?'.format(self.source)
        ans = self._inst.query(command)
        return float(ans)
    
    @offset.setter
    def offset(self, offset):
        command = 'SOUR{}:VOLT:OFFS {}'.format(self.source, offset)
        self._inst.write(command)

class AFG3xxxProxy(AFG3xxx):
    _visa_servername = None

    def __init__(self, cxn=None, **kwargs):
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        from visa_server.proxy import VisaProxy
        visa = VisaProxy(cxn[self._visa_servername])
        AFG3xxx.__init__(self, visa=visa, **kwargs)
