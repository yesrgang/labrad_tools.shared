"""
### BEGIN NODE INFO
[info]
name = si_demod
version = 1.0
description = 
instancename = si_demod

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from labrad.server import LabradServer
from labrad.server import setting
from labrad.wrappers import connectAsync
from twisted.internet import reactor
from twisted.internet.reactor import callInThread
from twisted.internet.reactor import callLater
from twisted.internet.defer import inlineCallbacks
from twisted.internet.defer import returnValue
import vxi11

class SiDemodServer(LabradServer):
    name = 'si_demod'
    
    def initServer(self):
        self.instr = vxi11.Instrument('192.168.1.58')
        self._get_frequency()

    @setting(1)
    def get_frequency(self, c):
        return self.frequency

    def _get_frequency(self):
        response = self.instr.ask('SOUR1:FREQ?')
	self.instr.local()
        self.frequency = 8 * float(response)
        callLater(60, self._get_frequency)

if __name__ == "__main__":
    from labrad import util
    server = SiDemodServer()
    util.runServer(server)
