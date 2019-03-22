import json
import numpy as np
import time
import visa

from visa_server.proxy import VisaProxy


class LDC80(object):
    gpib_address = None
    pro8_slot = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        print visa
        rm = visa.ResourceManager()
        rm.open_resource(self.gpib_address)
        self._rm = rm

    def _write_to_slot(self, command):
        slot_command = ':SLOT {};'.format(self.pro8_slot)
        self._rm.write(slot_command + command)
    
    def _query_to_slot(self, command):
        slot_command = ':SLOT {};'.format(self.pro8_slot)
        response = self._rm.query(slot_command + command)
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
        if response == ':LASER ON':
            return True
        elif response == ':LASER OFF':
            return False

    @state.setter
    def state(self, state):
        if state:
            command = ':LASER ON'
        else:
            command = ':LASER OFF'
        self._write_to_slot(command)

class LDC80Proxy(LDC80):
    def __init__(self, visa_server, **kwargs):
        global visa
        visa = VisaProxy(visa_server)
        LDC80.__init__(self, **kwargs)

        
