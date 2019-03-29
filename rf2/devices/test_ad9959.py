import labrad
from ad9959 import AD9959Proxy

class Device(AD9959Proxy):
    serial_servername = 'yesr5_serial'
    serial_port = 'COM24'
    arduino_address = 0
    channel_number = 1

cxn = labrad.connect()
device = Device(cxn)
#device.program_amplitude_ramp(1, 0.5, 1)
device.amplitude = 1
device.sweep = 'amplitude'
