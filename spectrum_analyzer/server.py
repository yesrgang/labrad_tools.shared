"""
### BEGIN NODE INFO
[info]
name = spectrum_analyzer
version = 1.0
description = 
instancename = spectrum_analyzer

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

class SpectrumAnalyzerServer(DeviceServer):
    """ Provides basic control for spectrum analyzers """
    name = 'spectrum_analyzer'

    @setting(10)
    def traces(self, c, request_json='{}'):
        """ get or update device traces """
        request = json.loads(request_json)
        response = self._traces(request)
        response_json = json.dumps(response)
        return response_json
        
    def _traces(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, trace in request.items():
            device_response = None
            try:
                device_response = self._trace(device_name, trace)
            except:
                self._reload_device(device_name, {})
                device_response = self._trace(device_name, trace)
            response.update({device_name: device_response})
        self._send_update({'traces': response})
        return response

    def _trace(self, name, trace):
        device = self._get_device(name)
        if trace:
            device.set_trace(trace)
        response = device.get_trace()
        return response
    
    @setting(11)
    def frequency_ranges(self, c, request_json='{}'):
        """ get or update device frequency_ranges """
        request = json.loads(request_json)
        response = self._frequency_ranges(request)
        response_json = json.dumps(response)
        return response_json
        
    def _frequency_ranges(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, frequency_range in request.items():
            device_response = None
            try:
                device_response = self._frequency_range(device_name, 
                                                        frequency_range)
            except:
                self._reload_device(device_name, {})
                device_response = self._frequency_range(device_name, 
                                                        frequency_range)
            response.update({device_name: device_response})
        self._send_update({'frequency_ranges': response})
        return response

    def _frequency_range(self, name, frequency_range):
        device = self._get_device(name)
        if frequency_range:
            device.set_frequency_range(frequency_range)
        response = device.get_frequency_range()
        return response

    @setting(12)
    def resolution_bandwidths(self, c, request_json='{}'):
        """ get or update device resolution_bandwidths """
        request = json.loads(request_json)
        response = self._resolution_bandwidths(request)
        response_json = json.dumps(response)
        return response_json
        
    def _resolution_bandwidths(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, resolution_bandwidth in request.items():
            device_response = None
            try:
                device_response = self._resolution_bandwidth(device_name, 
                                                             resolution_bandwidth)
            except:
                self._reload_device(device_name, {})
                device_response = self._resolution_bandwidth(device_name, 
                                                             resolution_bandwidth)
            response.update({device_name: device_response})
        self._send_update({'resolution_bandwidths': response})
        return response

    def _resolution_bandwidth(self, name, resolution_bandwidth):
        device = self._get_device(name)
        if resolution_bandwidth:
            device.set_resolution_bandwidth(resolution_bandwidth)
        response = device.get_resolution_bandwidth()
        return response

    @setting(13)
    def amplitude_scales(self, c, request_json='{}'):
        """ get or update device amplitude_scales """
        request = json.loads(request_json)
        response = self._amplitude_scales(request)
        response_json = json.dumps(response)
        return response_json
        
    def _amplitude_scales(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, amplitude_scale in request.items():
            device_response = None
            try:
                device_response = self._amplitude_scale(device_name, 
                                                             amplitude_scale)
            except:
                self._reload_device(device_name, {})
                device_response = self._amplitude_scale(device_name, 
                                                             amplitude_scale)
            response.update({device_name: device_response})
        self._send_update({'amplitude_scales': response})
        return response

    def _amplitude_scale(self, name, amplitude_scale):
        device = self._get_device(name)
        if amplitude_scale:
            device.set_amplitude_scale(amplitude_scale)
        response = device.get_amplitude_scale()
        return response

    @setting(14)
    def amplitude_offsets(self, c, request_json='{}'):
        """ get or update device amplitude_offsets """
        request = json.loads(request_json)
        response = self._amplitude_offsets(request)
        response_json = json.dumps(response)
        return response_json
        
    def _amplitude_offsets(self, request):
        if request == {}:
            active_devices = self._get_active_devices()
            request = {device_name: None for device_name in active_devices}
        response = {}
        for device_name, amplitude_offset in request.items():
            device_response = None
            try:
                device_response = self._amplitude_offset(device_name, 
                                                             amplitude_offset)
            except:
                self._reload_device(device_name, {})
                device_response = self._amplitude_offset(device_name, 
                                                             amplitude_offset)
            response.update({device_name: device_response})
        self._send_update({'amplitude_offsets': response})
        return response

    def _amplitude_offset(self, name, amplitude_offset):
        device = self._get_device(name)
        if amplitude_offset:
            device.set_amplitude_offset(amplitude_offset)
        response = device.get_amplitude_offset()
        return response

Server = SpectrumAnalyzerServer

if __name__ == '__main__':
    from labrad import util
    util.runServer(Server())
