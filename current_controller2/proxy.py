import json

class CurrentControllerServerProxy(object):
    def __init__(self, server):
        self.server = server

    @property
    def active_devices(self):
        response_json = self.server.get_active_devices()
        response = json.loads(response_json)
        return {device_name: CurrentControllerDeviceProxy(self.server, device_name)
                for device_name in response}
    
    @property
    def configured_devices(self):
        response_json = self.server.get_configured_devices()
        return json.loads(response_json)

    def initialize_devices(self, request={}):
        self.server.initialize_devices(json.dumps(request))

    def reload_devices(self, request={}):
        self.server.reload_devices(json.dumps(request))

class CurrentControllerDeviceProxy(object):
    def __init__(self, server, name):
        self.server = server
        self.name = name
    
    @property
    def state(self):
        request = {self.name: {'state': None}}
        response_json = self.server.get(json.dumps(request))
        response = json.loads(response_json)
        return response[self.name]['state']
    
    @state.setter
    def state(self, state):
        request = {self.name: {'state': state}}
        response_json = self.server.set(json.dumps(request))

    @property
    def shutter_state(self):
        request = {self.name: {'shutter_state': None}}
        response_json = self.server.get(json.dumps(request))
        response = json.loads(response_json)
        return response[self.name]['shutter_state']
    
    @shutter_state.setter
    def shutter_state(self, shutter_state):
        request = {self.name: {'shutter_state': shutter_state}}
        response_json = self.server.set(json.dumps(request))

    @property
    def current(self):
        request = {self.name: {'current': None}}
        response_json = self.server.get(json.dumps(request))
        response = json.loads(response_json)
        return response[self.name]['current']

    @current.setter
    def current(self, current):
        request = {self.name: {'current': current}}
        response_json = self.server.set(json.dumps(request))
    
    @property
    def power(self):
        request = {self.name: {'power': None}}
        response_json = self.server.get(json.dumps(request))
        response = json.loads(response_json)
        return response[self.name]['power']

    @power.setter
    def power(self, power):
        request = {self.name: {'power': power}}
        response_json = self.server.set(json.dumps(request))

    def warmup(self, method_request):
        request = {self.name: {'warmup': method_request}}
        self.server.call(json.dumps(request))
    
    def shutdown(self, method_request):
        request = {self.name: {'shutdown': method_request}}
        self.server.call(json.dumps(request))

#    @property
#    def devices(self):
#        response_json = self.server.get_active_devices()
#        return json.loads(response_json)

