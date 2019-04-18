import socket
import time

class LDC50(object):
    socket_address = None
    _current_range = (0.0, 153.0)
    _relock_stepsize = 0.001
    _relock_duration = 2

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _get_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect(self.socket_address)
        s.send('\n')
        s.send('ULOC 1\n')
        return s

    @property
    def current(self):
        s = self._get_socket()
        s.send('RILD?\n')
        response = s.recv(1024)
        s.close()
        current_ma = float(response.strip())
        return current_ma / 1e3

    @current.setter
    def current(self, current_a):
        current_ma = current_a * 1e3
        s = self._get_socket()
        s.send('SILD {}\n'.format(current_ma))
        s.close()

    @property
    def power(self):
        s = self._get_socket()
        s.send('RWPD?\n')
        response = s.recv(1024)
        s.close()
        power_mw = float(response.strip())
        return power_mw / 1e3

    def relock(self):
        current = self.current
        self.current = current + self._relock_stepsize
        time.sleep(self._relock_duration)
        self.current = current

    @property
    def state(self):
        s = self._get_socket()
        s.send('LDON?\n')
        response = s.recv(1024)
        s.close()
        return bool(int(response.strip()))

    @state.setter
    def state(self, state):
        s = self._get_socket()
        if state:
            s.send('LDON ON\n')
        else:
            s.send('LDON OFF\n')
        s.close()
