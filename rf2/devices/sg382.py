class SG382(object):
    vxi11_address = None
    source = None

    frequency_range = (1e6, 2e9)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'vxi11' not in globals():
            global vxi11
            import vxi11
        self._inst = vxi11.Instrument(self.vxi11_address)

    @property
    def frequency(self):
        command = 'FREQ?'
        ans = self._inst.ask(command)
        return float(ans)
    
    @frequency.setter
    def frequency(self, frequency):
        frequency = sorted([min(self.frequency_range), 
            max(self.frequency_range), frequency])[1]
        print frequency
        command = 'FREQ {}'.format(frequency)
        self._inst.write(command)
    
