"""
### BEGIN NODE INFO
[info]
name = frequency_counter
version = 1.0
description = 
instancename = frequency_counter

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
from labrad.server import setting

from device_server.server import DeviceServer

class FrequencyCounterServer(DeviceServer):
    name = 'frequency_counter'

    @setting(10)
    def frequencies(self, c, request_json='{}'):
        """ get or update device frequencies """
        request = json.loads(request_json)
        response = self._frequencies(request)
        response_json = json.dumps(response)
        return response_json
        
    def _frequencies(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, device_request in request:
            try:
                device_response = self._frequency(device_name, device_request)
            except:
                self._reload_device(device_name, {})
                device_response = self._frequency(device_name, device_request)
            response.update({device_name: device_response})
        self._send_update({'frequencies': response})
        return response

    def _frequency(self, name, request):
        device = self._get_device(name)
        response = device.get_frequency()
        return response

Server = FrequencyCounterServer

if __name__ == "__main__":
    from labrad import util
    util.runServer(Server())
