from rf.clients.rf_client import RFClient

class BetaClient(RFClient):
    servername = 'rf'
    name = 'beta'

    frequency_display_units = [(6, 'MHz')]
    frequency_digits = 3
    amplitude_display_units = [(0, 'dBm')]
    amplitude_digits = 2
    update_time = 100

    spinbox_width = 100

Client = BetaClient

if __name__ == '__main__':
    from PyQt4 import QtGui
    from rf.clients.rf_client import RFClient
    app = QtGui.QApplication([])
    import client_tools.qt4reactor as qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    widget = Client(reactor)
    widget.show()
    reactor.run()
