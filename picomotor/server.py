"""
### BEGIN NODE INFO
[info]
name = picomotor
version = 1.0
description = 
instancename = picomotor

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


class PicomotorServer(DeviceServer):
    name = 'picomotor'
    autostart = False
    
    @setting(10)
    def positions(self, c, request_json='{}'):
        """ get or update device positions """
        request = json.loads(request_json)
        response = self._positions(request)
        response_json = json.dumps(response)
        return response_json
        
    def _positions(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, position in request.items():
            try:
                device_response = self._position(device_name, position)
            except:
                self._reload_device(device_name, {})
                device_response = self._position(device_name, position)
            response.update({device_name: device_response})
        self._send_update({'positions': response})
        return response

    def _position(self, name, position):
        device = self._get_device(name)
        if position:
            device.set_position(position)
        response = device.get_position()
        return response
    
Server = PicomotorServer

if __name__ == '__main__':
    from labrad import util
    util.runServer(Server())
