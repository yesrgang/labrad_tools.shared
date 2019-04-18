import json
import numpy as np
import time

from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks

from client_tools.widgets import ClickableLabel, IntSpinBox

class PicomotorClient(QtGui.QGroupBox):
    name = None
    DeviceProxy = None
    updateID = np.random.randint(0, 2**31 - 1)
    spinboxWidth = 70
    positionRange = (-np.inf, np.inf)
    
    def __init__(self, reactor, cxn=None):
        QtGui.QDialog.__init__(self)
        self.reactor = reactor
        self.cxn = cxn
        reactor.callInThread(self.initialize)
        self.connectLabrad()
    
    def initialize(self):
        if self.cxn == None:
            import labrad
            self.cxn = labrad.connect(name=self.name)
        self.device = self.DeviceProxy(self.cxn)
        self.reactor.callFromThread(self.populateGUI)

    def populateGUI(self):
        self.nameLabel = ClickableLabel('<b>' + self.name + '</b>      ')
#        self.nameLabel.setFixedWidth(50)
        self.positionBox = IntSpinBox(self.positionRange)
        self.positionBox.setFixedWidth(self.spinboxWidth)
        
        self.layout = QtGui.QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.nameLabel, 0, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.positionBox, 0, 1)
        
        self.setWindowTitle('{}'.format(self.name))
        self.setLayout(self.layout)
        self.setFixedSize(80 + self.spinboxWidth, 40)
        self.setFixedSize(self.minimumSize())

        self.connectSignals()

    def connectSignals(self):
        self.nameLabel.clicked.connect(self.onNameLabelClick)
        self.positionBox.returnPressed.connect(self.onNewPosition)
    
    def onNameLabelClick(self):
        self.reactor.callInThread(self.getPosition)

    def onNewPosition(self):
        position = int(self.positionBox.value())
        self.reactor.callInThread(self.setPosition, position)

    def displayPosition(self, position):
        self.positionBox.display(position)

    def getPosition(self):
        position = self.device.position
        self.reactor.callFromThread(self.displayPosition, position)

    def setPosition(self, position):
        self.device.position = position
        self.reactor.callFromThread(self.displayPosition, position)
    
    @inlineCallbacks
    def connectLabrad(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(name=self.name)
        yield self.cxn.update.signal__signal(self.updateID)
        yield self.cxn.update.addListener(listener=self.receiveUpdate, source=None, 
                                          ID=self.updateID)
        yield self.cxn.update.register(self.name)
    
    def receiveUpdate(self, c, updateJson):
        update = json.loads(updateJson)
        position = update.get('position')
        if position is not None:
            self.displayPosition(position)
        
    def closeEvent(self, x):
        self.reactor.stop()

class MultipleClientContainer(QtGui.QWidget):
    name = None
    children = []

    def __init__(self, reactor, cxn=None):
        QtGui.QDialog.__init__(self)
        self.reactor = reactor
        self.cxn = cxn
        reactor.callInThread(self.initialize)
    
    def initialize(self):
        if self.cxn == None:
            import labrad
            self.cxn = labrad.connect(name=self.name)
        self.reactor.callFromThread(self.populateGUI)
 
    def populateGUI(self):
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum,
                                       QtGui.QSizePolicy.Minimum)
        self.setSizePolicy(sizePolicy)

        self.layout = QtGui.QHBoxLayout()
        self.clientList = []
        for columnClients in self.children:
            column = QtGui.QWidget()
            internalLayout = QtGui.QVBoxLayout()
            for clientClass in columnClients:
                client = clientClass(self.reactor, self.cxn)
                self.clientList.append(client)
                internalLayout.addWidget(client)
            column.setLayout(internalLayout)
            self.layout.addWidget(column)

        self.setWindowTitle(self.name)
        self.setLayout(self.layout)

        self.setFixedSize(self.minimumSize())

        self.reactor.callInThread(self.getAll)

    def getAll(self):
        time.sleep(1)
        for client in self.clientList:
            self.reactor.callFromThread(client.positionBox.clearFocus)
            client.getPosition()

    def closeEvent(self, x):
        self.reactor.stop()

if __name__ == '__main__':
    from picomotor2.devices import image_x

    class Client(PicomotorClient):
        name = 'image_x'
        DeviceProxy = image_x.DeviceProxy
    
    from PyQt4 import QtGui
    app = QtGui.QApplication([])
    from client_tools import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor

    widget = Client(reactor)
    widget.show()
    reactor.run()
