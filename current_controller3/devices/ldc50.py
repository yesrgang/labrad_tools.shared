import socket

class LDC50(object):
    socket_address = None
    current_range = (0.0, 153.0)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def current(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect(self.socket_address)
        s.send('\n')
        s.send('ULOC 1\n')
        s.send('RILD?\n')
        response = s.recv(1024)
        s.close()
        return float(response.strip())

    @current.setter
    def current(self, current):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect(self.socket_address)
        s.send('\n')
        s.send('ULOC 1\n')
        s.send('SILD {}\n'.format(current))
        s.close()

    @property
    def power(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect(self.socket_address)
        s.send('\n')
        s.send('ULOC 1\n')
        s.send('RWPD?\n')
        response = s.recv(1024)
        s.close()
        return float(response.strip())


    @property
    def state(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect(self.socket_address)
        s.send('\n')
        s.send('ULOC 1\n')
        s.send('LDON?\n')
        response = s.recv(1024)
        s.close()
        return float(response.strip())

    @state.setter
    def state(self, state):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect(self.socket_address)
        s.send('\n')
        s.send('ULOC 1\n')
        if state:
            s.send('LDON ON\n')
        else:
            s.send('LDON OFF\n')
        s.close()