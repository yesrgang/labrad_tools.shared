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
    name = '%LABRADNODE%_ok2'

    def initServer(self):
        self._open_xems = {}

    def _get_xem(self, serial=None):
        if serial not in self._open_xems:
            devices = ok.okCFrontPanelDevices()
            self._open_xems[serial] = devices.Open(serial)
        return self._open_xems[serial]

    @setting(10, serial='s')
    def close(self, c, serial):
        xem = self._get_xem(serial)
        xem.Close()
        del self._open_xems[serial]
    
    @setting(11, serial='s', strFilename='s')
    def configure_fpga(self, c, serial, strFilename):
        xem = self._get_xem(serial)
        xem.ConfigureFPGA(strFilename)

    @setting(12)
    def get_count(self, c):
        devices = ok.okCFrontPanelDevices()
        return devices.GetCount()

    @setting(13, num='i')
    def get_serial(self, c, num):
        devices = ok.okCFrontPanelDevices()
        return devices.GetSerial(num)
    
    @setting(14, serial='s', epAddr='i')
    def get_wire_out_value(self, c, serial, epAddr):
        xem = self._get_xem(serial)
        return xem.GetWireOutValue(epAddr)
    
    @setting(15, serial='s', epAddr='i', mask='w')
    def is_triggered(self, c, serial, epAddr, mask):
        xem = self._get_xem(serial)
        return xem.IsTriggered(epAddr, mask)
    
    @setting(16, serial='s')
    def open(self, c, serial=''):
        devices = ok.okCFrontPanelDevices()
        xem = devices.Open(serial)
        serial = xem.GetSerialNumber()
        self._open_xems[serial] = xem
        return serial

    @setting(17, serial='s')
    def open_by_serial(self, c, serial):
        fp = ok.okCFrontPanel()
        xem = fp.OpenBySerial(serial)
        self._open_xems[serial] = serial
    
    @setting(18, serial='s', epAddr='i', val='i', mask='w')
    def set_wire_in_value(self, c, serial, epAddr, val, mask):
        xem = self._get_xem(serial)
        xem.SetWireInValue(epAddr, val, mask)
    
    @setting(19, serial='s')
    def update_trigger_outs(self, c, serial):
        xem = self._get_xem(erial)
        xem.UpdateTriggerOuts()
    
    @setting(20, serial='s')
    def update_wire_ins(self, c, serial):
        xem = self._get_xem(serial)
        xem.UpdateWireIns()
    
    @setting(21, serial='s')
    def update_wire_outs(self, c, serial):
        xem = self._get_xem(serial)
        xem.UpdateWireOuts()
    
    @setting(22, serial='s', epAddr='i', data='*y')
    def write_to_pipe_in(self, c, serial, epAddr, data):
        xem = self._get_xem(serial)
        xem.WriteToPipeIn(epAddr, bytearray(data))

Server = OKServer

if __name__ == "__main__":
    from labrad import util
    util.runServer(Server())
