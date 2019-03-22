from ello import ELLO
from serial_server.proxy import SerialProxy

class ELLOProxy(ELLO):
    def __init__(self, serial_server, serial_port=None, address=0):
        serial = SerialProxy(serial_server)
        super(ELLOProxy, self).__init__(serial_port, address)
