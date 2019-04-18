import vxi11

class Agilent335xx(object):
    _source = None
    _vxi11_address = None
    _available_waveforms = []
    
    def __init__(self, **kwargs):
        try:
            vxi11 = kwargs.pop('vxi11')
        except KeyError:
            import vxi11
        for key, value in kwargs.items():
            setattr(self, key, value)
        self._inst = vxi11.Instrument(self._vxi11_address)

    def _setup(self)
        command = 'SOUR{}:DATA:VOL:CLE'.format(self.source)
        self._inst.write(command)
        for waveform in self._available_waveforms:
            command = 'MMEM:LOAD:DATA{} "{}"'.format(self.source, waveform)
            self._inst.write(command)
            command = 'SOUR{}:FUNC:ARB "{}"'.format(self.source, waveform)
            self._inst.write(command)
    
    @property
    def waveform(self):
        command = 'SOUR{}:FUNC:ARB?'.format(self.source)
        return self._inst.ask(command)

    @waveform.setter
    def waveform(self, waveform):
        if waveform not in self._available_waveforms:
            message = 'waveform "{}" not configured'.format(waveform)
            raise Exception(message)
        command = 'SOUR{}:FUNC:ARB "{}"'.format(self.source, waveform)
        self._inst.write(command)

class Agilent335xxProxy(Agilent335xx):
    _vxi11_servername = None

    def __init__(self, cxn=None, **kwargs):
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        from vxi11_server.proxy import Vxi11Proxy
        vxi11_server = cxn[self._vxi11_servername]
        vxi11 = Vxi11Proxy(vxi11_server)
        Agilent335xx.__init__(self, vxi11=vxi11, **kwargs)
