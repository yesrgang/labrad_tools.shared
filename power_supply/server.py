"""
### BEGIN NODE INFO
[info]
name = power_supply
version = 1.0
description = 
instancename = power_supply

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


class PowerSupplyServer(DeviceServer):
    """ Provides basic control for current controllers """
    name = 'power_supply'

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
    def voltages(self, c, request_json='{}'):
        """ get output voltages """
        request = json.loads(request_json)
        response = self._voltages(request)
        response_json = json.dumps(response)
        return response_json
        
    def _voltages(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, device_request in request.items():
            device_response = None
            try:
                device_response = self._voltage(device_name, device_request)
            except:
                self._reload_device(device_name, {})
                device_response = self._voltage(device_name, device_request)
            response.update({device_name: device_response})
        self._send_update({'voltages': response})
        return response

    def _voltage(self, name, request):
        device = self._get_device(name)
        response = device.get_voltage()
        return response
    
    @setting(12)
    def currents(self, c, request_json='{}'):
        """ get output currents """
        request = json.loads(request_json)
        response = self._currents(request)
        response_json = json.dumps(response)
        return response_json
        
    def _currents(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, device_request in request.items():
            device_response = None
            try:
                device_response = self._current(device_name, device_request)
            except:
                self._reload_device(device_name, {})
                device_response = self._current(device_name, device_request)
            response.update({device_name: device_response})
        self._send_update({'currents': response})
        return response

    def _current(self, name, request):
        device = self._get_device(name)
        response = device.get_current()
        return response
    
    @setting(13)
    def voltage_limits(self, c, request_json='{}'):
        """ get or update device voltage_limits """
        request = json.loads(request_json)
        response = self._voltage_limits(request)
        response_json = json.dumps(response)
        return response_json
        
    def _voltage_limits(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, voltage_limit in request.items():
            device_response = None
            try:
                device_response = self._voltage_limit(device_name, state)
            except:
                self._reload_device(device_name, {})
                device_response = self._voltage_limit(device_name, state)
            response.update({device_name: device_response})
        self._send_update({'voltage_limits': response})
        return response

    def _voltage_limit(self, name, state):
        device = self._get_device(name)
        if voltage_limit:
            device.set_voltage_limit(state)
        response = device.get_voltage_limit()
        return response
    
    @setting(14)
    def current_limits(self, c, request_json='{}'):
        """ get or update device current_limits """
        request = json.loads(request_json)
        response = self._current_limits(request)
        response_json = json.dumps(response)
        return response_json
        
    def _current_limits(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, current_limit in request.items():
            device_response = None
            try:
                device_response = self._current_limit(device_name, state)
            except:
                self._reload_device(device_name, {})
                device_response = self._current_limit(device_name, state)
            response.update({device_name: device_response})
        self._send_update({'current_limits': response})
        return response

    def _current_limit(self, name, state):
        device = self._get_device(name)
        if current_limit:
            device.set_current_limit(state)
        response = device.get_current_limit()
        return response
    
Server = PowerSupplyServer

if __name__ == '__main__':
    from labrad import util
    util.runServer(Server())
