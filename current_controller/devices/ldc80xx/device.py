import json
import numpy as np
import time

from twisted.internet.reactor import callInThread

from device_server.device import DefaultDevice
from visa_server.proxy import VisaProxy

class Ldc80xx(DefaultDevice):
    """ thorlabs ldc80xx device 

    write to gpib bus with write_to_slot and query with query_with_slot
    so that multiple instances of this device don't get confused responses
    from thr PRO8
    """
    gpib_servername = None
    gpib_address = None

    pro8_slot = None

    current_ramp_duration = 5
    current_ramp_num_points = 10
    current_range = (0.0, 0.153)
    current_stepsize = 1e-4
    default_current = 0

    update_parameters = ['state', 'current', 'power']

    def initialize(self, config):
        super(Ldc80xx, self).initialize(config)
        self.connect_to_labrad()
        
        self.visa_server = self.cxn[self.gpib_servername]
        visa = VisaProxy(self.visa_server)
        rm = visa.ResourceManager()
        rm.open_resource(self.gpib_address)
        self.visa = visa
        self.rm = rm

        self.get_parameters()
    
    def get_parameters(self):
        self.state = self.get_state()
        self.current = self.get_current()
        self.power = self.get_power()
        update = {p + 's': {self.name: getattr(self, p)} for p in self.update_parameters}
        self.server._send_update((update))

    def write_to_slot(self, command):
        slot_command = ':SLOT {};'.format(self.pro8_slot)
        self.rm.write(slot_command + command)
    
    def query_to_slot(self, command):
        slot_command = ':SLOT {};'.format(self.pro8_slot)
        response = self.rm.query(slot_command + command)
        return response

    def get_current(self):
        command = ':ILD:SET?'
        response = self.query_to_slot(command)
        return float(response[9:])

    def set_current(self, current):
        min_current = self.current_range[0]
        max_current = self.current_range[1]
        current = sorted([min_current, current, max_current])[1]
        command = ':ILD:SET {}'.format(current)
        
        self.write_to_slot(command)
        self.power = self.get_power()

    def get_power(self):
        command = ':POPT:ACT?'
        response = self.query_to_slot(command)
        return float(response[10:])
    
    def set_power(self, power):
        # could raise ldc80xx SetPowerError: cannot set ldc80xx power
        pass

    def get_state(self):
        command = ':LASER?'
        response = self.query_to_slot(command)
        if response == ':LASER ON':
            return True
        elif response == ':LASER OFF':
            return False

    def set_state(self, state):
        if state:
            command = ':LASER ON'
        else:
            command = ':LASER OFF'
        self.write_to_slot(command)

    def dial_current(self, stop):
        start = self.get_current()
        currents = np.linspace(start, stop, self.current_ramp_num_points+1)[1:]
        dt = float(self.current_ramp_duration) / self.current_ramp_num_points
        for current in currents: 
            self.set_current(current)
            time.sleep(dt)
    
    def warmup(self, request={}):
        callInThread(self.do_warmup)
    
    def do_warmup(self):
        self.set_state(True)
        self.dial_current(self.default_current)
        time.sleep(.1)
        self.get_parameters()

    def shutdown(self, request={}):
        callInThread(self.do_shutdown)

    def do_shutdown(self):
        self.dial_current(min(self.current_range))
        self.set_state(False)
        time.sleep(.1)
        self.get_parameters()
