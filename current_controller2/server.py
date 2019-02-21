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

#    @setting(10, device_name='s', state_request='b', returns='b')
#    def state(self, c, device_name, state_request=None):
#        device = self._get_device(device_name)
#        if state_request:
#            device.state = state_request
#        state_response = device.state
#        return state_response
#
#    @setting(11, device_name='s', shutter_state_request='b', returns='b')
#    def shutter_state(self, c, device_name, shutter_state_request=None):
#        device = self._get_device(device_name)
#        if shutter_state_request:
#            device.shutter_state = shutter_state_request
#        shutter_state_response = device.shutter_state
#        return shutter_state_response
#
#    @setting(12, device_name='s', current='v', returns='v')
#    def current(self, c, device_name, current=None):
#        device = self._get_device(device_name)
#        current = device.current(current)
#        return current
#    
#    @setting(13, device_name='s', power='v', returns='v')
#    def power(self, c, device_name, power=None):
#        device = self._get_device(device_name)
#        power = device.power(power)
#        return power
#
#    @setting(14, device_name='s', warmup='v', returns='v')
#    def warmup(self, c, device_name, warmup=None):
#        device = self._get_device(device_name)
#        warmup = device.warmup(warmup)
#        return warmup
#    
#    @setting(15, device_name='s', shutdown='v', returns='v')
#    def shutdown(self, c, device_name, shutdown=None):
#        device = self._get_device(device_name)
#        shutdown = device.shutdown(shutdown)
#        return shutdown

Server = CurrentControllerServer

if __name__ == '__main__':
    from labrad import util
    reactor.suggestThreadPoolSize(5)
    util.runServer(Server())
