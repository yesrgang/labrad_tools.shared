import numpy as np
import time

from twisted.internet.reactor import callInThread

from device_server.device import DefaultDevice
from serial_server.proxy import SerialProxy


class AOSenseECDL(DefaultDevice):
    serial_servername = None
    serial_address = None
    serial_timeout = 0.05
    serial_baudrate = 115200
    
    current_ramp_duration = 5 # [s]
    current_ramp_num_points = 10 # [s]
    default_diode_current = None # [mA]
    diode_current_range = (10.0, 200.0) # [mA]

    piezo_voltage_range = (0.0, 125.0) # [V]
    
    update_parameters = ['state', 'diode_current', 'piezo_voltage']

    def initialize(self, config):
        super(AOSenseECDL, self).initialize(config)
        self.connect_to_labrad()
        self.serial_server = self.cxn[self.serial_servername]

        serial = SerialProxy(self.serial_server)
        ser = serial.Serial(self.serial_address)
        ser.timeout = self.serial_timeout
        ser.baudrate = self.serial_baudrate
        self.ser = ser

        self.get_parameters()

    def get_parameters(self):
        self.state = self.get_state()
        self.diode_current = self.get_diode_current()
        self.piezo_voltage = self.get_piezo_voltage()
        update = {p + 's': {self.name: getattr(self, p)} for p in self.update_parameters}
        self.server._send_update((update))

    def get_state(self):
        command = 'LASER\r\n'
        self.ser.write(command)
        response = self.ser.readlines()
        if 'OFF' not in response[0]:
            state = True
        else:
            state = False
        return state

    def set_state(self, state):
        if state:
            command = 'LASER ON\r\n'
        else:
            command = 'LASER OFF\r\n'
        self.ser.write(command)
        response = self.ser.readlines()

    def get_diode_current(self):
        command = 'ILA\r\n'
        self.ser.write(command)
        response = self.ser.readlines()
        current = float(response[0].split('=')[-1])
        return current

    def set_diode_current(self, current):
        min_current = min(self.diode_current_range)
        max_current = max(self.diode_current_range)
        current = sorted([min_current, current, max_current])[1]
        command = 'ILA {}\r\n'.format(round(current, 5))
        self.ser.write(command)
        response = self.ser.readlines()
        
    def get_piezo_voltage(self):
        command = 'UPZ\r\n'
        self.ser.write(command)
        response = self.ser.readlines()
        voltage = float(response[0].split('=')[-1])
        return voltage
    
    def set_piezo_voltage(self, voltage):
        min_voltage = self.piezo_voltage_range[0]
        max_voltage = self.piezo_voltage_range[1]
        voltage = sorted([min_voltage, voltage, max_voltage])[1]
        command = 'UPZ {}\r\n'.format(voltage)
        self.ser.write(command)
        response = self.ser.readlines()
    
    def dial_current(self, stop):
        start = self.get_diode_current()
        currents = np.linspace(start, stop, self.current_ramp_num_points+1)[1:]
        dt = float(self.current_ramp_duration) / self.current_ramp_num_points
        for current in currents: 
            self.set_diode_current(current)
            time.sleep(dt)

    def warmup(self, request):
        callInThread(self.do_warmup)
    
    def do_warmup(self):
        self.set_state(True)
        self.dial_current(self.default_diode_current)
        time.sleep(1)
        self.get_parameters()
    
    def shutdown(self, request):
        callInThread(self.do_shutdown)

    def do_shutdown(self):
        self.dial_current(min(self.diode_current_range))
        self.set_state(False)
        time.sleep(5)
        self.get_parameters()
