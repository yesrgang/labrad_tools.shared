import struct

from serial_server.proxy import SerialProxy

class AD9959(object):
    """ serial wrapper for controlling AD9956

    this class is meant to be inherited:

    class MyDDS(AD9956):
        serial_port = '/dev/ttyACM0'
        arduino_address = 0
        channel_num = 0

    >> my_dds = MyDDS()

    frequencies can then be programmed via
    >> my_dds.frequency = 100e6
    or read via
    >> my_dds.frequency
    """
    serial_port = None
    serial_timeout = 0.05
    serial_baudrate = 9600
    
    arduino_address = None
    channel_number = None

    sysclk = 500e6

    csr = int(0x00)
    cfr = int(0x03)
    cftr0 = int(0x04)
    acr = int(0x06)
    lsrrr = int(0x07)
    rdr = int(0x08)
    fdr = int(0x09)
    cr1 = int(0x0A)
    
    amplitude_range = [0, 1]
    frequency_range = [0, sysclk / 2]
    
    def __init__(self, **kwargs):
        self.mode = 'single'
        self._rate = 1
        self._sweep = None
        self._frequency = None
        self._start_frequency = None
        self._stop_frequency = None
        self._amplitude = None
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'serial' not in globals():
            global serial
            import serial
        ser = serial.Serial(self.serial_port)
        ser.timeout = self.serial_timeout
        ser.baudrate = self.serial_baudrate
        self._ser = ser
    
    def _make_instruction_set(self, register, data):
        if data is not None:
            ins = [58, self.arduino_address, len(data)+1, register] + data
            ins_sum = sum(ins[1:])
            ins_sum_bin = bin(ins_sum)[2:].zfill(8)
            lowest_byte = ins_sum_bin[-8:]
            checksum = int('0b'+str(lowest_byte), 0)
            ins.append(checksum)
            return [chr(i) for i in ins]
        else:
            return []

    def _make_csw(self):
        """ return channel select word """
        if self.channel_number > 3:
            raise TypeError
        return [(2**int(self.channel_number) << 4) + 2]

    def _make_cfw(self, sweep):
        """ return channel function  word """
        cfw = [None, None, None]
        if sweep == 'frequency':
            afp = 0b10
            linear_sweep_no_dwell = 0b0
            linear_sweep_enable = 0b1
#        elif sweep == 'amplitude':
#            afp = 0b01
#            linear_sweep_no_dwell = 0b0
#            linear_sweep_enable = 0b1
        elif sweep == 'phase':
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

    def _make_cftw(self, frequency):
        """ return frequency tuning word """
        if frequency is not None:
            cftw = hex(int(frequency * 2.**32 / self.sysclk))[2:].zfill(8) # 32-bit dac
            return [int('0x' + cftw[i:i+2], 0) for i in range(0, 8, 2)]

    def _make_acw(self, amplitude, ramp=False):
        if amplitude is not None:
            """ return amplitude control word """
            asf = bin(int(amplitude * (2**10 - 1)))[2:].zfill(10)
            part_1 = int(asf[:2], 2)
            part_2 = int(asf[2:], 2)
            if ramp:
                return [1] + [216 + part_1] + [part_2]
            else:
                return [0] + [16 + part_1] + [part_2]
    
    def _make_lsrrw(self, rate):
        """ return linear sweep ramp rate word """
        t_step = max(-rate, 1)
        return [t_step, t_step]
    
    def _make_rdw(self, rate):
        """ return rising delta word """
        step_size = max(rate, 1)
        return list(struct.unpack('4B', struct.pack('I', step_size))[::-1])

    def _make_fdw(self, rate):
        """ return falling delta word """
        step_size = max(rate, 1)
        return list(struct.unpack('4B', struct.pack('I', step_size))[::-1])
    
    def _write_to_registers(self):
        csw = self._make_csw()
        cfw = self._make_cfw(self._sweep)
        if self._sweep == 'frequency':
            cftw0 = self._make_cftw(self._start_frequency)
        else:
            cftw0 = self._make_cftw(self._frequency)
        if self._sweep == 'amplitude':
            acw = self._make_acw(self._amplitude, ramp=True)
        else:
            acw = self._make_acw(self._amplitude)
        lsrrw = self._make_lsrrw(self._rate)
        rdw = self._make_rdw(self._rate)
        fdw = self._make_fdw(self._rate)
        cw1 = self._make_cftw(self._stop_frequency)
        
        instruction_set = []
        instruction_set += self._make_instruction_set(self.csr, csw)
        instruction_set += self._make_instruction_set(self.cfr, cfw)
        instruction_set += self._make_instruction_set(self.cftr0, cftw0)
        instruction_set += self._make_instruction_set(self.acr, acw)
        instruction_set += self._make_instruction_set(self.lsrrr, lsrrw)
        instruction_set += self._make_instruction_set(self.rdr, rdw)
        instruction_set += self._make_instruction_set(self.fdr, fdw)
        instruction_set += self._make_instruction_set(self.cr1, cw1)
        
        command = ''.join(instruction_set)
        self._ser.write(command)
    
    @property
    def amplitude(self):
        return self._amplitude

    @amplitude.setter
    def amplitude(self, amplitude):
        self._amplitude = amplitude
        self._write_to_registers()
    
    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, frequency):
        self._frequency = frequency
        self._write_to_registers()
    
    @property
    def sweep(self):
        return self._sweep

    @sweep.setter
    def sweep(self, sweep):
        self._sweep = sweep
        self._write_to_registers()

    def program_frequency_ramp(self, start, stop, rate):
        self._start_frequency = start
        self._stop_frequency = stop
        self._rate = rate
        self._write_to_registers()

class AD9959Proxy(AD9959):
    serial_servername = None

    def __init__(self, cxn=None, **kwargs):
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        global serial
        serial_server = cxn[self.serial_servername]
        serial = SerialProxy(serial_server)
        AD9959.__init__(self, **kwargs)
