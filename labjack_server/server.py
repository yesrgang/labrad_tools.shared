"""
### BEGIN NODE INFO
[info]
name = labjack
version = 1.0
description = 
instancename = %LABRADNODE%_labjack

[startup]
cmdline = %PYTHON% %FILE%
timeout = 60

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""
from labjack import ljm
import json

from labrad.server import setting

from server_tools.threaded_server import ThreadedServer

class LabjackServer(ThreadedServer):
    """ Provides access to labjack T series using labjack-ljm """
    name = '%LABRADNODE%_labjack'
    
    @setting(10, deviceType='s', connectionType='s', identifier='s', returns='i')
    def open_s(self, c, deviceType, connectionType, identifier):
        return ljm.openS(deviceType, connectionType, identifier)
    
    @setting(11, handle='i', name='s', returns='?')
    def e_read_name(self, c, handle, name):
        return ljm.eReadName(handle, name)

Server = LabjackServer

if __name__ == "__main__":
    from labrad import util
    util.runServer(Server())
