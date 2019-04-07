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
from twisted.internet.defer import DeferredLock

from labrad.server import setting
from server_tools.threaded_server import ThreadedServer


class OKServer(ThreadedServer):
    name = '%LABRADNODE%_ok2'

    def initServer(self):
        self._open_xems = {}

    def _get_xem(self, serial=None):
        if serial not in self._open_xems:
            devices = ok.okCFrontPanelDevices()
            xem = devices.Open(serial)
            xem._lock = DeferredLock()
            self._open_xems[serial] = xem
        return self._open_xems[serial]

    @setting(10, serial='s')
    def close(self, c, serial):
        xem = self._get_xem(serial)
        xem._lock.acquire()
        xem.Close()
        del self._open_xems[serial]
    
    @setting(11, serial='s', strFilename='s')
    def configure_fpga(self, c, serial, strFilename):
        xem = self._get_xem(serial)
        xem._lock.acquire()
        xem.ConfigureFPGA(strFilename)
        xem._lock.release()

    @setting(12)
    def get_count(self, c):
        devices = ok.okCFrontPanelDevices()
        return devices.GetCount()
    
    @setting(13)
    def get_device_count(self, c):
        fp = ok.okCFrontPanel()
        return fp.GetDeviceCount()
    
    @setting(14, num='i')
    def get_device_list_serial(self, c, num):
        fp = ok.okCFrontPanel()
        fp.GetDeviceCount()
        return fp.GetDeviceListSerial(num)

    @setting(15, num='i')
    def get_serial(self, c, num):
        devices = ok.okCFrontPanelDevices()
        return devices.GetSerial(num)
    
    @setting(16, serial='s', epAddr='i')
    def get_wire_in_value(self, c, serial, epAddr):
        xem = self._get_xem(serial)
        xem._lock.acquire()
        val = xem.GetWireInValue(epAddr)
        xem._lock.release()
        return val
    
    @setting(17, serial='s', epAddr='i')
    def get_wire_out_value(self, c, serial, epAddr):
        xem = self._get_xem(serial)
        xem._lock.acquire()
        val = xem.GetWireOutValue(epAddr)
        xem._lock.release()
        return val
    
    @setting(18, serial='s', epAddr='i', mask='w')
    def is_triggered(self, c, serial, epAddr, mask):
        xem = self._get_xem(serial)
        xem._lock.acquire()
        is_triggered = xem.IsTriggered(epAddr, mask)
        xem._lock.release()
        return is_triggered
    
    @setting(19, serial='s')
    def open(self, c, serial=''):
        if serial not in self._open_xems:
            devices = ok.okCFrontPanelDevices()
            xem = devices.Open(serial)
            serial = xem.GetSerialNumber()
            xem._lock = DeferredLock()
            self._open_xems[serial] = xem
        return serial

    @setting(20, serial='s')
    def open_by_serial(self, c, serial):
        if serial not in self._open_xems:
            fp = ok.okCFrontPanel()
            fp.GetDeviceCount()
            success = fp.OpenBySerial(serial)
            fp._lock = DeferredLock()
            self._open_xems[serial] = fp
        return serial
    
    @setting(21, serial='s', epAddr='i', val='i', mask='w')
    def set_wire_in_value(self, c, serial, epAddr, val, mask):
        print epAddr, val
        xem = self._get_xem(serial)
        xem._lock.acquire()
        xem.SetWireInValue(epAddr, val)#, mask)
#        self._open_xems[serial].SetWireInValue(epAddr, val)#, mask)
        xem._lock.release()
    
    @setting(22, serial='s')
    def update_trigger_outs(self, c, serial):
        xem = self._get_xem(serial)
        xem._lock.acquire()
        xem.UpdateTriggerOuts()
        xem._lock.release()
    
    @setting(23, serial='s')
    def update_wire_ins(self, c, serial):
        print 'u'
        xem = self._get_xem(serial)
        xem._lock.acquire()
        xem.UpdateWireIns()
        xem._lock.release()
    
    @setting(24, serial='s')
    def update_wire_outs(self, c, serial):
        xem = self._get_xem(serial)
        xem._lock.acquire()
        xem.UpdateWireOuts()
        xem._lock.release()
    
    @setting(25, serial='s', epAddr='i', data='*w')
    def write_to_pipe_in(self, c, serial, epAddr, data):
        print len(data)
        xem = self._get_xem(serial)
        xem._lock.acquire()
        xem.WriteToPipeIn(epAddr, bytearray(data))
        xem._lock.release()
    
    @setting(26)
    def go(self, c):
        one_s = [128, 240, 250, 2]
        all_hi = [255] * 8 + one_s
        all_lo = [0] * 8 + one_s
        stop = [0] * 12
        
        fp = ok.FrontPanel()
        fp.GetDeviceCount()
        ser = fp.GetDeviceListSerial(0)
        fp.OpenBySerial(ser)
        fp.ConfigureFPGA('/home/srgang/labrad_tools.srq/ok_server/bit/digital_sequencer-v3.2.bit')
        fp.SetWireInValue(0x00, 3)
        fp.UpdateWireIns()
        fp.WriteToPipeIn(0x80, bytearray((all_hi + all_lo) * 10 + stop))
        fp.SetWireInValue(0x00, 1)
        fp.UpdateWireIns()
        fp._lock = DeferredLock()
        self._open_xems[ser] = fp
#        fp.SetWireInValue(0x01, 1)
#        fp.UpdateWireIns()

        self.fp = fp

    @setting(27)
    def go2(self, c):
        self._open_xems['1840000NUZ'].SetWireInValue(1, 1)
#        self.fp.SetWireInValue(0x01, 1)
        self.fp.UpdateWireIns()

Server = OKServer

if __name__ == "__main__":
    from labrad import util
    util.runServer(Server())
