class NF8742(object):
    _socket_address = None
    _socket_timeout = 0.1
    _socket_buffersize = 1024

    _controller_axis = None
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'socket' not in globals():
            global socket
            import socket

    def _get_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self._socket_timeout)
        s.connect(self._socket_address)
        return s

    @property
    def position(self):
        s = self._get_socket()
        command = '{}PA?\n'.format(self._controller_axis)
        s.send(command)
        response = s.recv(self._socket_buffersize)
        s.close()
        response = response.strip()
        response = response.replace('\xff\xfb\x01\xff\xfb\x03', '')
        return int(response)
    
    @position.setter
    def position(self, position):
        s = self._get_socket()
        command = '{}PA{}\n'.format(self._controller_axis, position)
        s.send(command)
        s.close()

class NF8742Proxy(NF8742):
    _socket_servername = None

    def __init__(self, cxn=None, **kwargs):
        from socket_server.proxy import SocketProxy
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        global socket
        socket_server = cxn[self._socket_servername]
        socket = SocketProxy(socket_server)
        NF8742.__init__(self, **kwargs)
