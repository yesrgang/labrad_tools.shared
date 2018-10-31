"""
### BEGIN NODE INFO
[info]
name = stepper_motor
version = 1.0
description = 
instancename = stepper_motor

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

import json

from labrad.server import setting

from device_server.server import DeviceServer

class StepperMotorServer(DeviceServer):
    name = 'stepper_motor'

    @setting(10, 'move absolute', position='i', returns='i')
    def move_absolute(self, c, position=None):
        device = self.get_selected_device(c)
        if position is not None:
            yield device.move_absolute(position)
        returnValue(position)
    
    @setting(10)
    def move_absolute(self, c, request_json='{}'):
        """ get or update device move_absolute """
        request = json.loads(request_json)
        response = self._move_absolute(request)
        response_json = json.dumps(response)
        return response_json
        
    def _move_absolute(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, position in request.items():
            device_response = None
            try:
                device_response = self.device_move_absolute(device_name, position)
            except:
                self._reload_device(device_name, {})
                device_response = self.device_move_absolute(device_name, position)
            response.update({device_name: device_response})
        self._send_update({'move_absolute': response})
        return response

    def device_move_absolute(self, name, position):
        device = self._get_device(name)
        if position:
            device.move_absolute(position)
    
    @setting(11)
    def toggle_absolute(self, c, request_json='{}'):
        """ get or update device toggle_absolute """
        request = json.loads(request_json)
        response = self._toggle_absolute(request)
        response_json = json.dumps(response)
        return response_json
        
    def _toggle_absolute(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, positions in request.items():
            device_response = None
            try:
                device_response = self.device_toggle_absolute(device_name, positions)
            except:
                self._reload_device(device_name, {})
                device_response = self.device_toggle_absolute(device_name, positions)
            response.update({device_name: device_response})
        self._send_update({'toggle_absolute': response})
        return response

    def device_toggle_absolute(self, name, positions):
        device = self._get_device(name)
        if positions:
            device.toggle_absolute(**positions)

Server = StepperMotorServer

if __name__ == "__main__":
    from labrad import util
    util.runServer(Server())
