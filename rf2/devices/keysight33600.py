class FrequencyOutOfBoundsError(Exception):
    pass

class AmplitudeOutOfBoundsError(Exception):
    pass

class Keysight33600(object):
    _amplitude_range = None
    _amplitude_units = 'dBm'
    _frequency_range = (0, float('inf'))
    _source = None
    _vxi11_address = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'vxi11' not in globals():
            global vxi11
            import vxi11
        self._inst = vxi11.Instrument(self._vxi11_address)

    @property
    def state(self):
        command = 'OUTP{}?'.format(self._source)
        ans = self._inst.ask(command)
        return bool(int(ans))
    
    @state.setter
    def state(self, state):
        command = 'OUTP{}:STAT {}'.format(self._source, int(bool(state)))
        self._inst.write(command)

    @property
    def frequency(self):
        command = 'SOUR{}:FREQ?'.format(self._source)
        ans = self._inst.ask(command)
        return float(ans)
    
    @frequency.setter
    def frequency(self, frequency):
        if frequency < min(self._frequency_range) or frequency > max(self._frequency_range):
            raise FrequencyOutOfBoundsError(frequency)
        command = 'SOUR{}:FREQ {}'.format(self._source, frequency)
        self._inst.write(command)
    
    @property
    def amplitude(self):
        command = 'SOUR{}:VOLT?'.format(self._source)
        ans = self._inst.ask(command)
        return float(ans)
    
    @amplitude.setter
    def amplitude(self, amplitude):
        if amplitude < min(self._amplitude_range) or amplitude > max(self._amplitude_range):
            raise AmplitudeOutOfBoundsError(amplitude)
        command = 'SOUR{}:VOLT {} {}'.format(self._source, amplitude, self._amplitude_units)
        self._inst.write(command)

class Keysight33600Proxy(Keysight33600):
    _vxi11_servername = None

    def __init__(self, cxn=None, **kwargs):
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        from vxi11_server.proxy import Vxi11Proxy
        global vxi11
        vxi11 = Vxi11Proxy(cxn[self._vxi11_servername])
        Keysight33600.__init__(self, **kwargs)
