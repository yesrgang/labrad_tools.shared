"""
### BEGIN NODE INFO
[info]
name = ok
version = 1.0
description = 
instancename = %LABRADNODE%_ok

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
import ok

from labrad.server import setting
from server_tools.threaded_server import ThreadedServer


class OKServer(ThreadedServer):
    name = '%LABRADNODE%_ok'

    def _get_xem(self, realm='', serial=None):
        #devices = ok.okCFrontPanelDevices(realm=realm)
        devices = ok.okCFrontPanelDevices()
        return devices.GetSerial(serial)
    
    @setting(10, realm='s', serial=['s', '?'], strFilename='s')
    def configure_fpga(self, c, realm, serial, strFilename):
        xem = self._get_xem(realm, serial)
        xem.ConfigureFPGA(strFilename)

    @setting(11, realm='s')
    def get_count(self, c, realm):
        #devices = ok.okCFrontPanelDevices(realm=realm)
        devices = ok.okCFrontPanelDevices()
        return devices.GetCount()

    @setting(12, realm='s', num='i')
    def get_serial(self, c, realm, num):
        #devices = ok.okCFrontPanelDevices(realm=realm)
        devices = ok.okCFrontPanelDevices()
        return devices.GetSerial(num)
    
    @setting(13, realm='s', serial=['s', '?'], epAddr='i')
    def get_wire_out_value(self, c, realm, serial, epAddr):
        xem = self._get_xem(realm, serial)
        return xem.GetWireOutValue(epAddr)
    
    @setting(14, realm='s', serial=['s', '?'], epAddr='i', mask='i')
    def is_triggered(self, c, realm, serial, epAddr, mask):
        xem = self._get_xem(realm, serial)
        return xem.IsTriggered(epAddr, mask)
    
    @setting(15, realm='s', serial=['s', '?'])
    def open(self, c, realm, serial):
        #devices = ok.okCFrontPanelDevices(realm=realm)
        devices = ok.okCFrontPanelDevices()
        xem = devices.Open(serial)

    @setting(16, serial=['s', '?'])
    def open_by_serial(self, c, serial):
        fp = ok.okCFrontPanel()
        xem = fp.OpenBySerial(serial)
    
    @setting(17, realm='s', serial=['s', '?'], epAddr='i', val='i', mask='i')
    def set_wire_in_value(self, c, realm, serial, epAddr, val, mask):
        xem = self._get_xem(realm, serial)
        xem.SetWireInValue(epAddr, val, mask)
    
    @setting(18, realm='s', serial=['s', '?'])
    def update_trigger_outs(self, c, realm, serial):
        xem = self._get_xem(realm, serial)
        xem.UpdateTriggerOuts()
    
    @setting(19, realm='s', serial=['s', '?'])
    def update_wire_ins(self, c, realm, serial):
        xem = self._get_xem(realm, serial)
        xem.UpdateWireIns()
    
    @setting(20, realm='s', serial=['s', '?'])
    def update_wire_outs(self, c, realm, serial):
        xem = self._get_xem(realm, serial)
        xem.UpdateWireOuts()
    
    @setting(21, realm='s', serial='s', epAddr='i', data='*y')
    def write_to_pipe_in(self, c, realm, serial, epAddr, data):
        xem = self._get_xem(realm, serial)
        xem.WriteToPipeIn(epAddr, bytearray(data))

Server = OKServer

if __name__ == "__main__":
    from labrad import util
    util.runServer(Server())
