class AD9854(object):
    serial_port = None
    serial_timeout = 0.5
    serial_baudrate = 4800
    
    arduino_address = None

    sysclk = 300e6
    freg = int(0x02)
    areg = int(0x08)
    
    amplitude_range = (0, 1)
    frequency_range=(1e3, 140e6)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'serial' not in globals():
            import serial
        ser = serial.Serial(self.serial_port)
        ser.timeout = self.serial_timeout
        ser.baudrate = self.serial_baudrate
        self._ser = ser

    def _make_ftw(self, frequency):
        ftw = hex(int(frequency * 2.**32 / self.sysclk))[2:].zfill(8) # 32-bit dac
        return [int('0x' + ftw[i:i+2], 0) for i in range(0, 8, 2)]

    def _make_atw(self, amplitude):
        atw =  hex(int(amplitude * (2**12 - 1)))[2:].zfill(4)
        return [int('0x'+atw[i:i+2], 0) for i in range(0, 4, 2)] + [0, 0]

    def _make_instruction_set(self, register, data):
        ins = [58, self.arduino_address, len(data)+1, register] + data
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
        ftw = self._make_ftw(frequency)
        instruction_set = self._make_instruction_set(self.freg, ftw)
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
        atw = self._make_atw(amplitude)
        instruction_set = self._make_instruction_set(self.areg, atw)
        command = ''.join(instruction_set)
        self._ser.write(command)
        response = self._ser.readline()
        if response.strip() != 'Roger that!':
            message = 'Error writing {} amplitude'.format(self.name)
            print message
        self._amplitude = amplitude

class AD9854Proxy(AD9854):
    serial_servername = None

    def __init__(self, cxn=None, **kwargs):
        from serial_server.proxy import SerialProxy
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        global serial
        serial_server = cxn[self.serial_servername]
        serial = SerialProxy(serial_server)
        AD9854.__init__(self, **kwargs)
