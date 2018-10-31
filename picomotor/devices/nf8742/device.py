import socket

from device_server.device import DefaultDevice


class NF8742(DefaultDevice):
    socket_address = None
    socket_timeout = 0.5
    socket_buffer_size = 1024

    controller_axis = None
    update_parameters = ['position']

    def initialize(self, config):
        super(NF8742, self).initialize(config)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.socket_timeout)
        self.socket.connect(self.socket_address)
        try:
            self.socket.recv(self.socket_buffer_size)
        except socket.timeout:
            pass

    def terminate(self):
        self.socket.close()

    def set_position(self, position):
        command = '{}PA{}\n'.format(self.controller_axis, position)
        self.socket.send(command)

    def get_position(self):
        command = '{}PA?\n'.format(self.controller_axis)
        self.socket.send(command)
        response = self.socket.recv(self.socket_buffer_size)
        return int(response.strip().replace(' ', ''))
