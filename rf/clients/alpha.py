from rf.clients.rf_client import RFClient

class AlphaClient(RFClient):
    servername = 'rf'
    name = 'alpha'

    frequency_display_units = [(9, 'GHz')]
    frequency_digits = 6
    amplitude_display_units = [(0, 'dBm')]
    amplitude_digits = 2
    update_time = 100

    spinbox_width = 100

Client = AlphaClient

if __name__ == '__main__':
    from PyQt4 import QtGui
    app = QtGui.QApplication([])
    import client_tools.qt4reactor as qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = Client(reactor)
    widget.show()
    reactor.run()
