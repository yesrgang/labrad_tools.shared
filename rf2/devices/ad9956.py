class FrequencyOutOfBoundsError(Exception):
    pass

class AmplitudeOutOfBoundsError(Exception):
    pass

class AD9956(object):
    """ serial wrapper for controlling AD9959
    
    example usage:
        class MyDDS(AD9959):
            _serial_port = '/dev/ACM0'
            _arduino_address = 0
            _channel_num = 0

        my_dds = MyDDS()

        # frequencies can then be programmed via
        my_dds.frequency = 100e6
        # or read via
        my_dds.frequency
    """
    _serial_port = None
    _serial_timeout = 0.05
    _serial_baudrate = 9600
    
    _arduino_address = None
    _channel_num = None

    _sysclk = 400e6
    _syncclk = _sysclk/4.0

    _cfr1_reg = int(0x00)
    _cfr2_reg = int(0x01)
    _rdftw_reg = int(0x02)
    _fdftw_reg = int(0x03)
    _rsrr_reg = int(0x04)
    _fsrr_reg = int(0x05)
    _flow_reg = int(0x06)
    _fhigh_reg = int(0x07)
       
    _frequency_range = [0, _sysclk / 2]
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'serial' not in globals():
            global serial
            import serial
        self._ser = serial.Serial(self._serial_port)
        self._ser.timeout = self._serial_timeout
        self._ser.baudrate = self._serial_baudrate
    
    def _make_instruction_set(self, register, data):
        ins = [58, self._arduino_address, len(data)+1, register] + data
        ins_sum = sum(ins[1:])
        ins_sum_bin = bin(ins_sum)[2:].zfill(8)
        lowest_byte = ins_sum_bin[-8:]
        checksum = int('0b'+str(lowest_byte), 0)
        ins.append(checksum)
        return [chr(i) for i in ins]

    def _make_cfr1w(self, mode):
        """ make control function register 1 word

        specifies either sweep mode or single frequency mode
        also ensures that we continue using 3-wire serial communication

        Args:
            mode (str): 'sweep' for frequency ramp, 'single' for single 
                frequency output.
        Returns:
            list of four bytes
        """

        linear_sweep_no_dwell = 0b0
        sdio_input_only = 0b1 #Configure for 3-wire serial communication
        cfr1w = [None, None, None, None]
        if mode == 'sweep':
            linear_sweep_enable = 0b1
        elif mode == 'single':
            linear_sweep_enable = 0b0
        else:
            linear_sweep_enable = 0b0

        cfr1w[0] = 0x00
        cfr1w[1] = linear_sweep_no_dwell + (linear_sweep_enable << 1) + 0x00
        cfr1w[2] = (sdio_input_only << 6) + 0x00
        cfr1w[3] = 0x00
        return cfr1w

    def _make_ftw(self, frequency):
        """ make frequency tuning word

        Args:
            frequency (float): frequency in units of Hz
        Returns:
            list of 8 bytes, specifying frequency in units of SYSCLK. By default 
            the phase is set to zero by setting the first two bytes to zero.
        """
        ftw = hex(int(frequency * 2.**48 / self._sysclk))[2:].zfill(16)
        return [int('0x' + ftw[i:i+2], 0) for i in range(0, 16, 2)]

    
    def _make_rsrrw(self, rate=1):
        """ make rising sweep ramp rate word

        Args:
            rate: (int) if <  0, increase time between sweep steps to 
                (rate / SYNC_CLK). minimum rate is 2**16 / SYNCCLK = 1525.879 Hz 
                for 400 MHz SYSCLK.
        Returns:
            list of 2 bytes, specifying sweep step rate in units of SYNCCLK.
        """
        t_step = max(-rate, 1)
        rsrww = hex(int(t_step))[2:].zfill(4)
        return [int('0x' + rsrww[i:i+2], 0) for i in range(0, 4, 2)]

    def _make_fsrrw(self, rate=1):
        """ make falling sweep ramp rate word

        Args:
            rate: (int) if <  0, increase time between sweep steps to 
                (rate / SYNC_CLK). minimum rate is 2**16 / SYNCCLK = 1525.879 Hz 
                for 400 MHz SYSCLK.
        Returns:
            list of 2 bytes, specifying sweep step rate in units of SYNCCLK.
        """
        t_step = max(-rate, 1)
        fsrww = hex(int(t_step))[2:].zfill(4)
        return [int('0x' + fsrww[i:i+2], 0) for i in range(0, 4, 2)]
    
    def _make_rdftw(self, rate):
        """ make rising delta frequency tuning word 

        Args: 
            rate: frequency step of ramp in Hz. rdftw given by 
                int(freq*SYSCLK/2*24). the minimum step size is 930 mHz for a 
                400 MHz clock. given frequency will be scaled to the nearest 
                integer multiple of the minimum step size
        Returns:
            list of 4 bytes, MSB first, of ramp down word
        """
        step_size = max(rate, 1) 
        rdftw = hex(int(step_size))[2:].zfill(6)
        return [int('0x' + rdftw[i:i+2], 0) for i in range(0, 6, 2)]

    def _make_fdftw(self, rate):
        """ make falling delta frequency tuning word 

        Args: 
            freq (float): frequency step of ramp in Hz. fdftw given by 
                int(freq*SYSCLK/2*24) the minimum step size is 93 mHz for a 400 
                MHz clock. given frequency will be scaled to the nearest integer 
                multiple of the minimum step size
        Returns:
            list of 4 bytes, MSB first, of ramp down word
        """
        step_size = max(rate, 1) 
        fdftw = hex(int(step_size))[2:].zfill(6)
        return [int('0x' + fdftw[i:i+2], 0) for i in range(0, 6, 2)]
    
    def _program_linear_ramp(self, start=None, stop=None, rate=1):
        """ program triggerable ramp.

        Args:
            start (float): frequency [Hz] corresponding to logic low
            stop (float): frequency [Hz] corresponding to logic high
            rate (int): if > 0, number of sys_clk (100 MHz) cycles per step
                0-65535 (2**16). if < 0, step size from 0-16777215 (2**24)
        Returns:
            None
        """
        if rate == None:
            rate = 1
        if stop >= start:
            ftw_start = self._make_ftw(start) # Write start frequency to pcr0
            ftw_stop = self._make_ftw(stop) # Write stop frequency to pcr1
            cfr1w = self._make_cfr1w('sweep') # Enable sweep mode
            rsrr = self._make_rsrrw(rate)
            fsrr = self._make_fsrrw(rate)
            rdw = self._make_rdftw(rate)
            fdw = self._make_fdftw(rate)
            instruction_set = (
                self._make_instruction_set(self._cfr1_reg, cfr1w)
                + self._make_instruction_set(self._rdftw_reg, rdw)
                + self._make_instruction_set(self._fdftw_reg, fdw)
                + self._make_instruction_set(self._rsrr_reg, rsrr)
                + self._make_instruction_set(self._fsrr_reg, fsrr)
                + self._make_instruction_set(self._flow_reg, ftw_start) 
                + self._make_instruction_set(self._fhigh_reg, ftw_stop) 
                )
            command = ''.join(instruction_set)
            self._ser.write(command)
        else:
            message = "End frequency must be greater than start frequency."
            raise Exception(message)

    def set_frequency(self, frequency, board=0, output='low'):
        """ select single frequency output mode at specified frequency

        Args:
            frequency: (float) frequency in units of Hz
        Returns:
            None
        """
        if frequency < min(self._frequency_range) or frequency > max(self._frequency_range):
            raise FrequencyOutOfBoundsError(frequency)
        cfr1w = self._make_cfr1w('single') 
        ftw = self._make_ftw(frequency) 
        if output == 'high':
            instruction_set = (
                self._make_instruction_set(self._arduino_address, self._cfr1_reg, cfr1w)
                + self._make_instruction_set(self._arduino_address, self._fhigh_reg, ftw)
                )
        else:
            instruction_set = (
                self._make_instruction_set(self._arduino_address, self._cfr1_reg, cfr1w)
                + self._make_instruction_set(self._arduino_address, self._flow_reg, ftw)
                )        
        command = ''.join(instruction_set)
        self._ser.write(command)
        
        if output == 'low':
            self.frequency_low = frequency
        else:
            self.frequency_high = frequency

    @property 
    def frequency(self):
        """ float: programmed freqeuncy for 'single' frequency mode """
        return self._frequency
    
    @property
    def ramp_frequencies(self):
        """ (float, float): programmed freqeuncies in 'ramp' frequency mode """
        return self._low_frequency, self._high_frequency

class AD9956Proxy(AD9956):
    _serial_servername = None

    def __init__(self, cxn=None, **kwargs):
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        from serial_server.proxy import SerialProxy
        global serial
        serial = SerialProxy(cxn[self._serial_servername])
        AD9956.__init__(self, **kwargs)
