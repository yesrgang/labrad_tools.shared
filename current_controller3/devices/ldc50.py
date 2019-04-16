import socket

class LDC50(object):
    socket_address = None
    _current_range = (0.0, 153.0)
    _relock_stepsize = 0.001

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
        current_ma = float(response.strip())
        return current_ma / 1e3

    @current.setter
    def current(self, current_a):
        current_ma = current_a * 1e3
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect(self.socket_address)
        s.send('\n')
        s.send('ULOC 1\n')
        s.send('SILD {}\n'.format(current_ma))
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
        power_mw = float(response.strip())
        return power_mw / 1e3

    def relock(self):
        current = self.current
        self.current = current + self._relock_stepsize
        self.current = current

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
