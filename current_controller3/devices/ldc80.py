from visa_server2.proxy import VisaProxy


class LDC80(object):
    gpib_address = None
    pro8_slot = None
    current_range = (0.0, 0.153)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'visa' not in globals():
            global visa
            import visa
        rm = visa.ResourceManager()
        self._inst = rm.open_resource(self.gpib_address)

    def _write_to_slot(self, command):
        slot_command = ':SLOT {};'.format(self.pro8_slot)
        self._inst.write(slot_command + command)
    
    def _query_to_slot(self, command):
        slot_command = ':SLOT {};'.format(self.pro8_slot)
        response = self._inst.query(slot_command + command)
        return response
    
    @property
    def current(self):
        command = ':ILD:SET?'
        response = self._query_to_slot(command)
        return float(response[9:])
    
    @current.setter
    def current(self, request):
        min_current = self.current_range[0]
        max_current = self.current_range[1]
        request = sorted([min_current, request, max_current])[1]
        command = ':ILD:SET {}'.format(request)
        self._write_to_slot(command)
    
    @property
    def power(self):
        command = ':POPT:ACT?'
        response = self._query_to_slot(command)
        power = float(response[10:])
        return power

    @property
    def state(self):
        command = ':LASER?'
        response = self._query_to_slot(command)
        if response.strip() == ':LASER ON':
            return True
        elif response.strip() == ':LASER OFF':
            return False

    @state.setter
    def state(self, state):
        if state:
            command = ':LASER ON'
        else:
            command = ':LASER OFF'
        self._write_to_slot(command)

class LDC80Proxy(LDC80):
    gpib_servername = None

    def __init__(self, cxn=None, **kwargs):
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        global visa
        gpib_server = cxn[self.gpib_servername]
        visa = VisaProxy(gpib_server)
        LDC80.__init__(self, **kwargs)
