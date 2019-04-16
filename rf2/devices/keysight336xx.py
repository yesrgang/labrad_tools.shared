class Keysight336xx(object):
    _amplitude_range = None
    _amplitude_units = 'dBm'
    _frequency_range = None
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
        frequency = sorted([min(self._frequency_range), 
            max(self._frequency_range), frequency])[1]
        command = 'SOUR{}:FREQ {}'.format(self._source, frequency)
        self._inst.write(command)
    
    @property
    def amplitude(self):
        command = 'SOUR{}:VOLT?'.format(self._source)
        ans = self._inst.ask(command)
        return float(ans)
    
    @amplitude.setter
    def amplitude(self, amplitude):
        amplitude = sorted([min(self._amplitude_range), 
            max(self._amplitude_range), amplitude])[1]
        command = 'SOUR{}:VOLT {} {}'.format(self._source, amplitude, self._amplitude_units)
        self._inst.write(command)

class Keysight336xxProxy(Keysight336xx):
    _vxi11_servername = None

    def __init__(self, cxn=None, **kwargs):
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        global vxi11
        from vxi11_server.proxy import Vxi11Proxy
        vxi11_server = cxn[self._vxi11_servername]
        vxi11 = Vxi11Proxy(vxi11_server)
        Keysight336xx.__init__(self, **kwargs)
