#"""
#### BEGIN NODE INFO
#[info]
#name = visa
#version = 1.0
#description = 
#instancename = visa
#
#[startup]
#cmdline = %PYTHON% %FILE%
#timeout = 60
#
#[shutdown]
#message = 987654321
#timeout = 5
#### END NODE INFO
#"""
import visa

from labrad.server import setting

from server_tools.threaded_server import ThreadedServer

class VisaServer(ThreadedServer):
    """ Provides access to USB/GPIB resources using pyvisa """
    name = '%LABRADNODE%_visa2'

    def initServer(self):
        self._rm = visa.ResourceManager()
        super(VisaServer, self).initServer()
    
    @setting(10, query='s', returns='*s')
    def list_resources(self, c, query='?*::INSTR'):
        return self._rm.list_resources()
    
    @setting(11, resource_name='s', mode='i')
    def control_ren(self, c, resource_name, mode):
        inst = self._rm.open_resource(resource_name)
        inst.control_ren(mode)
    
    @setting(12, resource_name='s', termination='s', encoding='s', returns='s')
    def read(self, c, resource_name, termination=None, encoding=None):
        inst = self._rm.open_resource(resource_name)
        return inst.read(termination, encoding)
    
    @setting(13, resource_name='s', returns='v')
    def get_timeout(self, c, resource_name, timeout=None):
        inst = self._rm.open_resource(resource_name)
        return inst.timeout

    @setting(14, resource_name='s', timeout='v')
    def set_timeout(self, c, resource_name, timeout):
        inst = self._rm.open_resource(resource_name)
        inst.timeout = timeout
    
    @setting(15, resource_name='s', message='s', delay='v', returns='s')
    def query(self, c, resource_name, message, delay=None):
        inst = self._rm.open_resource(resource_name)
        return inst.query(message, delay)

    @setting(16, resource_name='s', message='s', termination='s', encoding='s',
             returns='i')
    def write(self, c, resource_name, message, termination=None, encoding=None):
        inst = self._rm.open_resource(resource_name)
        return inst.write(message, termination, encoding)

Server = VisaServer

if __name__ == "__main__":
    from labrad import util
    util.runServer(Server())
