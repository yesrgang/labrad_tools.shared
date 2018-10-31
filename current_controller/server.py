"""
### BEGIN NODE INFO
[info]
name = current_controller
version = 1.0
description = 
instancename = current_controller

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""
import json

from labrad.server import setting

from device_server.server import DeviceServer

class CurrentControllerServer(DeviceServer):
    """ Provides basic control for current controllers """
    name = 'current_controller'

    @setting(10)
    def states(self, c, request_json='{}'):
        """ get or update device states """
        request = json.loads(request_json)
        response = self._states(request)
        response_json = json.dumps(response)
        return response_json
        
    def _states(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, state in request.items():
            device_response = None
            try:
                device_response = self._state(device_name, state)
            except:
                self._reload_device(device_name, {})
                device_response = self._state(device_name, state)
            response.update({device_name: device_response})
        self._send_update({'states': response})
        return response

    def _state(self, name, state):
        device = self._get_device(name)
        if state:
            device.set_state(state)
        response = device.get_state()
        return response

    @setting(11)
    def shutter_states(self, c, request_json='{}'):
        """ get or update device shutter_states """
        request = json.loads(request_json)
        response = self._shutter_states(request)
        response_json = json.dumps(response)
        return response_json
        
    def _shutter_states(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, shutter_state in request.items():
            device_response = None
            try:
                device_response = self._shutter_state(device_name, shutter_state)
            except:
                self._reload_device(device_name, {})
                device_response = self._shutter_state(device_name, shutter_state)
            response.update({device_name: device_response})
        self._send_update({'shutter_states': response})
        return response

    def _shutter_state(self, name, shutter_state):
        device = self._get_device(name)
        if shutter_state:
            device.set_shutter_state(shutter_state)
        response = device.get_shutter_state()
        return response
    
    @setting(12)
    def currents(self, c, request_json='{}'):
        """ get or update device currents """
        request = json.loads(request_json)
        response = self._currents(request)
        response_json = json.dumps(response)
        return response_json
        
    def _currents(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, current in request.items():
            device_response = None
            try:
                device_response = self._current(device_name, current)
            except:
                self._reload_device(device_name, {})
                device_response = self._current(device_name, current)
            response.update({device_name: device_response})
        self._send_update({'currents': response})
        return response

    def _current(self, name, current):
        device = self._get_device(name)
        if current:
            device.set_current(current)
        response = device.get_current()
        return response

    @setting(13)
    def powers(self, c, request_json='{}'):
        """ get or update device shutter states """
        request = json.loads(request_json)
        response = self._powers(request)
        response_json = json.dumps(response)
        return response_json
        
    def _powers(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, power in request.items():
            device_response = None
            try:
                device_response = self._power(device_name, power)
            except:
                self._reload_device(device_name, {})
                device_response = self._power(device_name, power)
            response.update({device_name: device_response})
        self._send_update({'powers': response})
        return response

    def _power(self, name, power):
        device = self._get_device(name)
        if power:
            device.set_power(power)
        response = device.get_power()
        return response

    @setting(14)
    def warmup(self, c, request_json='{}'):
        """ warmup devices """
        request = json.loads(request_json)
        response = self._warmup(request)
        response_json = json.dumps(response)
        return response_json
        
    def _warmup(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, device_request in request.items():
            device_response = None
            try:
                device_response = self._warmup_device(device_name, device_request)
            except:
                self._reload_device(device_name, {})
                device_response = self._warmup_device(device_name, device_request)
            response.update({device_name: device_response})
        self._send_update({'warmup': response})
        return response

    def _warmup_device(self, name, request):
        device = self._get_device(name)
        response = device.warmup(request)
        return response

    @setting(15)
    def shutdown(self, c, request_json='{}'):
        """ shutdown devices """
        request = json.loads(request_json)
        response = self._shutdown(request)
        response_json = json.dumps(response)
        return response_json
        
    def _shutdown(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, device_request in request.items():
            device_response = None
            try:
                device_response = self._shutdown_device(device_name, device_request)
            except:
                self._reload_device(device_name, {})
                device_response = self._shutdown_device(device_name, device_request)
            response.update({device_name: device_response})
        self._send_update({'shutdown': response})
        return response

    def _shutdown_device(self, name, request):
        device = self._get_device(name)
        response = device.shutdown(request)
        return response

Server = CurrentControllerServer

if __name__ == '__main__':
    from labrad import util
    util.runServer(Server())
