import json
import numpy as np
import sys
import time

from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from twisted.internet.defer import inlineCallbacks

from client_tools.connection import connection
from client_tools.widgets import IntSpinBox

class PicomotorClient(QtGui.QGroupBox):
    name = None
    servername = None

    def __init__(self, reactor, cxn=None):
        QtGui.QDialog.__init__(self)
        self.reactor = reactor
        self.cxn = cxn 
        self.update_id = np.random.randint(0, 2**31 - 1)
        self.initialize()

    @inlineCallbacks
    def initialize(self):
        if self.cxn is None:
            self.cxn = connection()
            yield self.cxn.connect()
        yield self.initialize_device()
        yield self.get_device_info()
        self.populateGUI()
        yield self.connectSignals()
        yield self.requestPosition()

    @inlineCallbacks
    def initialize_device(self):
        server = yield self.cxn.get_server(self.servername)
        request = {self.name: {}}
        yield server.initialize_devices(json.dumps(request))

    @inlineCallbacks
    def get_device_info(self):
        server = yield self.cxn.get_server(self.servername)
        request = {self.name: None}
        response_json = yield server.get_device_infos(json.dumps(request))
        response = json.loads(response_json)
        for key, value in response[self.name].items():
            setattr(self, key, value)
    
    def populateGUI(self):
        self.position_box = IntSpinBox(self.position_range)
        self.position_box.setFixedWidth(self.spinbox_width)
        self.position_box.display(0)
        
        self.layout = QtGui.QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        label = QtGui.QLabel('{}: '.format(self.name))
        label.setFixedWidth(50)

        self.layout.addWidget(label, 0, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.position_box, 0, 1)
        
        self.setWindowTitle('{} - {} - client'.format(self.servername, self.name))
        self.setLayout(self.layout)
        self.setFixedSize(80 + self.spinbox_width, 40)

    @inlineCallbacks
    def connectSignals(self):
        self.hasNewPosition = False
        server = yield self.cxn.get_server(self.servername)
        yield server.signal__update(self.update_id)
        yield server.addListener(listener=self.receive_update, source=None, 
                                 ID=self.update_id)
        yield self.cxn.add_on_connect(self.servername, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.servername, self.disable)

        self.position_box.returnPressed.connect(self.onNewPosition)
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.writeValues)
        self.timer.start(self.update_time)

    @inlineCallbacks
    def requestPosition(self, c=None):
        server = yield self.cxn.get_server(self.servername)
        request = {self.name: None}
        response = yield server.positions(json.dumps(request))
 
    def receive_update(self, c, signal_json):
        self.free = False
        signal = json.loads(signal_json)
        print signal
        for message_type, message in signal.items():
            device_message = message.get(self.name)
            if (message_type == 'positions') and (device_message is not None):
                self.position_box.display(device_message)
        self.free = True
    
    def onNewPosition(self):
        if self.free:
            self.hasNewPosition = True

    @inlineCallbacks
    def writeValues(self):
        if self.hasNewPosition:
            self.hasNewPosition = False
            server = yield self.cxn.get_server(self.servername)
            request = {self.name: int(self.position_box.value())}
            yield server.positions(json.dumps(request))
    
    def reinitialize(self):
        self.setDisabled(False)

    def disable(self):
        self.setDisabled(True)

    def closeEvent(self, x):
        self.reactor.stop()

class MultipleWidgetsContainer(QtGui.QWidget):
    name = None
    def __init__(self, reactor, cxn=None):
        QtGui.QDialog.__init__(self)
        self.reactor = reactor
        self.cxn = cxn
        self.populateGUI()
 
    def populateGUI(self):
        self.layout = QtGui.QHBoxLayout()
        for mirror_widgets in self.widgets:
            column = QtGui.QWidget()
            internal_layout = QtGui.QVBoxLayout()
            for WidgetClass in mirror_widgets:
                widget = WidgetClass(self.reactor)
                internal_layout.addWidget(widget)
            column.setLayout(internal_layout)
            self.layout.addWidget(column)
        self.setWindowTitle(self.name)
        self.setLayout(self.layout)

    def closeEvent(self, x):
        self.reactor.stop()
