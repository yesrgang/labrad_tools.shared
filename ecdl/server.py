"""
### BEGIN NODE INFO
[info]
name = ecdl
version = 1.0
description = 
instancename = ecdl

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


class ECDLServer(DeviceServer):
    name = 'ecdl'
    
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
    def diode_currents(self, c, request_json='{}'):
        """ get or update device diode_currents """
        request = json.loads(request_json)
        response = self._diode_currents(request)
        response_json = json.dumps(response)
        return response_json
        
    def _diode_currents(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, diode_current in request.items():
            device_response = None
            try:
                device_response = self._diode_current(device_name, diode_current)
            except:
                self._reload_device(device_name, {})
                device_response = self._diode_current(device_name, diode_current)
            response.update({device_name: device_response})
        self._send_update({'diode_currents': response})
        return response

    def _diode_current(self, name, diode_current):
        device = self._get_device(name)
        if diode_current:
            device.set_diode_current(diode_current)
        response = device.get_diode_current()
        return response
    
    @setting(12)
    def piezo_voltages(self, c, request_json='{}'):
        """ get or update device piezo_voltages """
        request = json.loads(request_json)
        response = self._piezo_voltages(request)
        response_json = json.dumps(response)
        return response_json
        
    def _piezo_voltages(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, piezo_voltage in request.items():
            device_response = None
            try:
                device_response = self._piezo_voltage(device_name, piezo_voltage)
            except:
                self._reload_device(device_name, {})
                device_response = self._piezo_voltage(device_name, piezo_voltage)
            response.update({device_name: device_response})
        self._send_update({'piezo_voltages': response})
        return response

    def _piezo_voltage(self, name, piezo_voltage):
        device = self._get_device(name)
        if piezo_voltage:
            device.set_piezo_voltage(piezo_voltage)
        response = device.get_piezo_voltage()
        return response
    
    @setting(13)
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

Server = ECDLServer

if __name__ == "__main__":
    from labrad import util
    util.runServer(Server())
