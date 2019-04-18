class FrequencyOutOfBoundsError(Exception):
    pass

class AmplitudeOutOfBoundsError(Exception):
    pass

class AD9854(object):
    _serial_port = None
    _serial_timeout = 0.5
    _serial_baudrate = 4800
    
    _arduino_address = None

    _sysclk = 300e6
    _freg = int(0x02)
    _areg = int(0x08)
    
    _amplitude_range = (0, 1)
    _frequency_range=(1e3, 140e6)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'serial' not in globals():
            global serial
            import serial
        self._ser = serial.Serial(self._serial_port)
        self._ser.timeout = self._serial_timeout
        self._ser.baudrate = self._serial_baudrate

    def _make_ftw(self, frequency):
        ftw = hex(int(frequency * 2.**32 / self._sysclk))[2:].zfill(8) # 32-bit dac
        return [int('0x' + ftw[i:i+2], 0) for i in range(0, 8, 2)]

    def _make_atw(self, amplitude):
        atw =  hex(int(amplitude * (2**12 - 1)))[2:].zfill(4)
        return [int('0x'+atw[i:i+2], 0) for i in range(0, 4, 2)] + [0, 0]

    def _make_instruction_set(self, register, data):
        ins = [58, self._arduino_address, len(data)+1, register] + data
        ins_sum = sum(ins[1:])
        ins_sum_bin = bin(ins_sum)[2:].zfill(8)
        lowest_byte = ins_sum_bin[-8:]
        checksum = int('0b'+str(lowest_byte), 0)
        ins.append(checksum)
        return [chr(i) for i in ins]
    
    @property
    def frequency(self):
        return self._frequency
   
    @frequency.setter
    def frequency(self, frequency):
        if frequency < min(self._frequency_range) or frequency > max(self._frequency_range):
            raise FrequencyOutOfBoundsError(frequency)
        ftw = self._make_ftw(frequency)
        instruction_set = self._make_instruction_set(self._freg, ftw)
        command = ''.join(instruction_set)
        self._ser.write(command)
        response = self._ser.readline()
        if response.strip() != 'Roger that!':
            message = 'Error writing {} frequency'.format(self.name)
            print message
        self._frequency = frequency
        
    @property
    def amplitude(self):
        return self._amplitude
    
    @amplitude.setter
    def amplitude(self, amplitude):
        if amplitude < min(self._amplitude_range) or amplitude > max(self._amplitude_range):
            raise AmplitudeOutOfBoundsError(amplitude)
        atw = self._make_atw(amplitude)
        instruction_set = self._make_instruction_set(self._areg, atw)
        command = ''.join(instruction_set)
        self._ser.write(command)
        response = self._ser.readline()
        if response.strip() != 'Roger that!':
            message = 'Error writing {} amplitude'.format(self.name)
            print message
        self._amplitude = amplitude

class AD9854Proxy(AD9854):
    _serial_servername = None

    def __init__(self, cxn=None, **kwargs):
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        from serial_server.proxy import SerialProxy
        global serial
        serial = SerialProxy(cxn[self._serial_servername])
        AD9854.__init__(self, **kwargs)
