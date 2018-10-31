import struct
import time

from twisted.internet import reactor

from device_server.device import DefaultDevice
from rf.devices.ad9959.helpers import get_instruction_set
from serial_server.proxy import SerialProxy


class AD9959(DefaultDevice):
    serial_servername = None
    serial_address = None
    serial_timeout = 0.05
    serial_baudrate = 9600
    
    board_num = None
    channel_num = None

    sysclk = 500e6

    csreg = int(0x00)
    cfreg = int(0x03)
    freg = int(0x04)
    areg = int(0x06)
    lsrr_reg = int(0x07)
    rdw_reg = int(0x08)
    fdw_reg = int(0x09)
    
    state = True
    
    amplitude = None
    default_amplitude = 1
    amplitude_range = [0, 1]
    
    frequency = None
    default_frequency = 0e6
    frequency_range = [0, sysclk / 2]

    update_parameters = ['state', 'frequency', 'amplitude']
    
    def initialize(self, config):
        super(AD9959, self).initialize(config)

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
    
    def make_csw(self):
        if self.channel > 3:
            message = 'channel {} is not in range [0, 3]'.format(self.channel)
            raise Exception(message)
        return [(2**int(self.channel) << 4) + 2]

    def make_cfw(self, mode):
        cfw = [None, None, None]
        if mode == 'frequency':
            afp = 0b10
            linear_sweep_no_dwell = 0b0
            linear_sweep_enable = 0b1
        elif mode == 'amplitude':
            afp = 0b01
            linear_sweep_no_dwell = 0b0
            linear_sweep_enable = 0b1
        elif mode == 'phase':
            afp = 0b11
            linear_sweep_no_dwell = 0b0
            linear_sweep_enable = 0b1
        else:
            afp = 0b00
            linear_sweep_no_dwell = 0b0
            linear_sweep_enable = 0b0

        cfw[0] = (afp << 6)
        cfw[1] = (linear_sweep_no_dwell << 7) + (linear_sweep_enable << 6) + 0x03
        cfw[2] = 0x0
        return cfw

    def make_ftw(self, frequency):
        ftw = hex(int(frequency * 2.**32 / self.sysclk))[2:].zfill(8) # 32-bit dac
        return [int('0x' + ftw[i:i+2], 0) for i in range(0, 8, 2)]

    def make_atw(self, amplitude):
        asf = bin(int(amplitude * (2**10 - 1)))[2:].zfill(10)
        part_1 = int(asf[:2], 2)
        part_2 = int(asf[2:], 2)
        return [0] + [16 + part_1] + [part_2]
    
    def make_lsrrw(self, rate):
        t_step = max(-rate, 1)
        return [t_step, t_step]
    
    def make_rdw(self, rate):
        step_size = max(rate, 1)
        return list(struct.unpack('4b', struct.pack('I', step_size))[::-1])

    def make_fdw(self, rate):
        step_size = max(rate, 1)
        return list(struct.unpack('4b', struct.pack('I', step_size))[::-1])
    
    def set_linear_ramp(self, start=None, stop=None, rate=None):
        csw = self.make_csw()
        if start is not None:
            cfw = self.make_cfw('frequency')
            ftw_start = self.make_ftw(start)
            ftw_stop = self.make_ftw(stop)
            instruction_set = (
                get_instruction_set(self.board_num, self.csreg, csw)
                + get_instruction_set(self.board_num, self.cfreg, cfw)
                + get_instruction_set(self.board_num, self.freg, ftw_start)
                + get_instruction_set(self.board_num, int(0x0A), ftw_stop)
                )

            command = ''.join(instruction_set)
            self.ser.write(command)
#            self.serial_server.write(self.serial_address, ''.join(instruction_set))

        if rate is not None: 
            lsrrw = self.make_lsrrw(rate)
            rdw = self.make_rdw(rate)
            fdw = self.make_fdw(rate)
        
            instruction_set = (
                get_instruction_set(self.board_num, self.csreg, csw)
                + get_instruction_set(self.board_num, self.lsrr_reg, lsrrw)
                + get_instruction_set(self.board_num, self.rdw_reg, rdw)
                + get_instruction_set(self.board_num, self.fdw_reg, fdw)
                )
        
            command = ''.join(instruction_set)
            self.ser.write(command)
#            self.serial_server.write(self.serial_address, ''.join(instruction_set))

    def set_state(self, state):
        pass

    def get_state(self):
        return True

    def set_frequency(self, frequency):
        csw = self.make_csw()
        ftw = self.make_ftw(frequency)
        instruction_set = (
            get_instruction_set(self.board_num, self.csreg, csw)
            + get_instruction_set(self.board_num, self.freg, ftw)
            )
        
        command = ''.join(instruction_set)
        self.ser.write(command)
#        self.serial_server.write(self.serial_address, ''.join(instruction_set))
       
        self.frequency = frequency

    def get_frequency(self):
        return self.frequency
        
    def set_amplitude(self, amplitude):
        csw = self.make_csw()
        atw = self.make_atw(amplitude)
        instruction_set = (
            get_instruction_set(self.board_num, self.csreg, csw)
            + get_instruction_set(self.board_num, self.areg, atw)
            )
        
        command = ''.join(instruction_set)
        self.ser.write(command)
#        self.serial_server.write(self.serial_address, ''.join(instruction_set))

        self.amplitude = amplitude

    def get_amplitude(self):
        return self.amplitude
