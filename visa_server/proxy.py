class VisaProxy(object):
    def __init__(self, visa_server):
        self.visa_server = visa_server

    def ResourceManager(self):
        rm = ResourceManagerProxy(self.visa_server)
        return rm

class ResourceManagerProxy(object):
    def __init__(self, visa_server):
        self.visa_server = visa_server

    def list_resources(self):
        return self.visa_server.get_available_interfaces()
    
    def open_resource(self, interface_id):
        self.interface_id = interface_id
        return self.visa_server.open_interface(self.interface_id)
    
    def GTL(self):
        if self.interface_id == None:
            raise Exception('must open resource first')
        return self.visa_server.go_to_local(self.interface_id)

    def query(self, command):
        if self.interface_id == None:
            raise Exception('must open resource first')
        return self.visa_server.query(self.interface_id, command)

    def read(self):
        if self.interface_id == None:
            raise Exception('must open resource first')
        return self.visa_server.read(self.interface_id)
    
    def timeout(self, command):
        if self.interface_id == None:
            raise Exception('must open resource first')
        return self.visa_server.timeout(self.interface_id, command)

    def write(self, command):
        if self.interface_id == None:
            raise Exception('must open resource first')
        return self.visa_server.write(self.interface_id, command)

