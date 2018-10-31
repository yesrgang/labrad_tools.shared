"""
### BEGIN NODE INFO
[info]
name = visa
version = 1
description =
instancename = %LABRADNODE%_visa

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
from labrad.server import setting

import visa

from hardware_interface_server.server import HardwareInterfaceServer
from hardware_interface_server.exceptions import InterfaceNotAvailable

VISA_LIBRARY = '@py'

class VISAServer(HardwareInterfaceServer):
    """Provides direct access to VISA-enabled hardware."""
    name = '%LABRADNODE%_visa'

    def _get_available_interfaces(self):
        rm = visa.ResourceManager(VISA_LIBRARY)
        available_interfaces = list(rm.list_resources())
        return available_interfaces

    def _get_open_interfaces(self):
        available_interfaces = self._get_available_interfaces()
        for interface_id in self.interfaces:
            if interface_id not in available_interfaces:
                del self.interfaces[interface_id]
        return self.interfaces.keys()
    
    def _open_interface(self, interface_id):
        rm = visa.ResourceManager(VISA_LIBRARY)
        if interface_id in self.interfaces:
            return
#            raise InterfaceAlreadyOpen(interface_id)
        try:
            inst = rm.open_resource(interface_id)
        except:
            raise InterfaceNotAvailable(interface_id)
        self.interfaces[interface_id] = inst
    
    def _close_interface(self, interface_id):
        inst = self._get_interface(interface_id)
        inst.close()
        del self.interfaces[interface_id]
    
    @setting(10)
    def go_to_local(self, c, interface_id):
        interface = self._get_interface(interface_id)
        interface.control_ren(6)

    @setting(11)
    def query(self, c, interface_id, command):
        interface = self._get_interface(interface_id)
        response = interface.query(command)
        return response.strip()

    @setting(12)
    def read(self, c, interface_id):
        interface = self._get_interface(interface_id)
        response = interface.read(command)
        return response.strip()
    
    @setting(13, interface_id='s', timeout='v')
    def timeout(self, c, interface_id, timeout=None):
        interface = self._get_interface(interface_id)
        if timeout is not None:
            interface.timeout = timeout
        return interface.timeout
    
    @setting(14)
    def write(self, c, interface_id, command):
        interface = self._get_interface(interface_id)
        interface.write(command)

Server = VISAServer

if __name__ == '__main__':
    from labrad import util
    util.runServer(Server())
