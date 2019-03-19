#"""
#### BEGIN NODE INFO
#[info]
#name = current_controller
#version = 1.0
#description = 
#instancename = current_controller
#
#[startup]
#cmdline = %PYTHON% %FILE%
#timeout = 20
#
#[shutdown]
#message = 987654321
#timeout = 5
#### END NODE INFO
#"""
import json

from labrad.server import setting
from twisted.internet import reactor

from device_server.server import DeviceServer


class CurrentControllerServer(DeviceServer):
    """ Provides basic control for current controllers """
    name = 'current_controller2'

Server = CurrentControllerServer

if __name__ == '__main__':
    from labrad import util
    reactor.suggestThreadPoolSize(5)
    util.runServer(Server())
