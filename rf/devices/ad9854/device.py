from twisted.internet import reactor
import time

from device_server.device import DefaultDevice
from rf.devices.ad9854.helpers import get_instruction_set
from serial_server.proxy import SerialProxy

class AD9854(DefaultDevice):
    serial_servername = None
    serial_address = None
    serial_timeout = 0.5
    serial_baudrate = 4800
    
    address = None

    sysclk = 300e6
    freg = int(0x02)
    areg = int(0x08)
    
    state = True
    
    amplitude = None
    default_amplitude = 1
    amplitude_range = (0, 1)
    
    frequency = None
    default_frequency = 80e6
    frequency_range=(1e3, 140e6)

    update_parameters = ['state', 'frequency', 'amplitude']

    def make_ftw(self, frequency):
        ftw = hex(int(frequency * 2.**32 / self.sysclk))[2:].zfill(8) # 32-bit dac
        return [int('0x' + ftw[i:i+2], 0) for i in range(0, 8, 2)]

    def make_atw(self, amplitude):
        atw =  hex(int(amplitude * (2**12 - 1)))[2:].zfill(4)
        return [int('0x'+atw[i:i+2], 0) for i in range(0, 4, 2)] + [0, 0]

    def initialize(self, config):
        super(AD9854, self).initialize(config)
        self.connect_to_labrad()
        self.serial_server = self.cxn[self.serial_servername]

        serial = SerialProxy(self.serial_server)
        ser = serial.Serial(self.serial_address)
        ser.timeout = self.serial_timeout
        ser.baudrate = self.serial_baudrate
        self.ser = ser

        time.sleep(0.2)
        reactor.callInThread(self.delayed_call, 5, self.set_frequency, self.default_frequency)
        reactor.callInThread(self.delayed_call, 5.1, self.set_frequency, self.default_frequency)

    def delayed_call(self, delay, func, *args):
        time.sleep(delay)
        func(*args)
    
    def set_state(self, state):
        pass

    def get_state(self):
        return True

    def set_frequency(self, frequency):
        ftw = self.make_ftw(frequency)
        instruction_set = get_instruction_set(self.subaddress, self.freg, ftw)
        command = ''.join(instruction_set)
        self.ser.write(command)
        response = self.ser.readline()
#        self.serial_server.write(self.serial_address, ''.join(instruction_set))
#        response = self.serial_server.readline(self.serial_address)
        if response.strip() != 'Roger that!':
            message = 'Error writing {} frequency'.format(self.name)
            print message
        self.frequency = frequency

    def get_frequency(self):
        return self.frequency
        
    def set_amplitude(self, amplitude):
        atw = self.make_atw(amplitude)
#        for b in get_instruction_set(self.subaddress, self.areg, atw):
#            self.serial_server.write(self.serial_address, b)
        instruction_set = get_instruction_set(self.subaddress, self.areg, atw)
        command = ''.join(instruction_set)
        self.ser.write(command)
        response = self.ser.readline()
#        self.serial_server.write(self.serial_address, ''.join(instruction_set))
#        response = self.serial_server.readline(self.serial_address)
        if response.strip() != 'Roger that!':
            message = 'Error writing {} amplitude'.format(self.name)
            print message
        self.amplitude = amplitude

    def get_amplitude(self):
        return self.amplitude

