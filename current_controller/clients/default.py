import json
import numpy as np
import sys

from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from twisted.internet.defer import inlineCallbacks

from client_tools.connection import connection

class ParameterLabel(QtGui.QLabel):
    clicked = QtCore.pyqtSignal()
    
    def mousePressEvent(self, x):
        self.clicked.emit()
    

class CurrentControllerClient(QtGui.QGroupBox):
    mouseHover = pyqtSignal(bool)
    state = None
    qt_style = 'Gtk+'
    i = 0
    
    def __init__(self, reactor, cxn=None):
        QtGui.QDialog.__init__(self)
        self.reactor = reactor
        self.cxn = cxn
        self.connect()

    @inlineCallbacks
    def connect(self):
        try:
            if self.cxn is None:
                self.cxn = connection()
                cname = '{} - {} - client'.format(self.servername, self.name)
                yield self.cxn.connect(name=cname)
            yield self.getDeviceInfo()
            self.populateGUI()
            yield self.connectSignals()
            yield self.requestValues()
        except Exception, e:
            print e
            raise

    @inlineCallbacks
    def getDeviceInfo(self):
        server = yield self.cxn.get_server(self.servername)
        request = {self.name: None}
        yield server.initialize_devices(json.dumps(request))
        device_info_json = yield server.get_device_infos(json.dumps(request))
        device_info = json.loads(device_info_json)
        for key, value in device_info[self.name].items():
            setattr(self, key, value)

    def populateGUI(self):
        self.state_button = QtGui.QPushButton()
        self.state_button.setCheckable(1)
        self.current_label = ParameterLabel('Current [A]: ')
        self.current_box = QtGui.QDoubleSpinBox()
        self.current_box.setKeyboardTracking(False)
        self.current_box.setRange(*self.current_range)
        self.current_box.setSingleStep(self.current_stepsize)
        self.current_box.setDecimals(abs(int(np.floor(np.log10(self.current_stepsize)))))
        self.current_box.setAccelerated(True)
        self.power_label = ParameterLabel('Power [mW]: ')
        self.power_box = QtGui.QDoubleSpinBox()
        self.power_box.setReadOnly(True)
        self.power_box.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.power_box.setDecimals(4)
        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(QtGui.QLabel('<b>'+self.name+'</b>'), 1, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.state_button, 1, 1)
        self.layout.addWidget(self.current_label, 2, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.current_box, 2, 1)
        self.layout.addWidget(self.power_label, 3, 0, 1, 1, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.power_box, 3, 1)
        self.setLayout(self.layout)
        self.setFixedSize(200, 120)

    @inlineCallbacks
    def connectSignals(self):
        self.hasNewState = False
        self.hasNewCurrent = False
        self.hasNewPower = False
        self.update_id = np.random.randint(0, 2**31 - 1)
        server = yield self.cxn.get_server(self.servername)
        yield server.signal__update(self.update_id)
        yield server.addListener(listener=self.receive_update, source=None, 
                                 ID=self.update_id)
        yield self.cxn.add_on_connect(self.servername, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.servername, self.disable)

        self.state_button.released.connect(self.onNewState)
        self.current_box.valueChanged.connect(self.onNewCurrent)
        
        #self.setMouseTracking(True)
        #self.mouseHover.connect(self.requestValues)
        self.power_label.clicked.connect(self.requestPower)
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.writeValues)
        self.timer.start(self.update_time)

    @inlineCallbacks
    def requestValues(self, c=None):
        yield self.requestState()
        yield self.requestCurrent()
        yield self.requestPower()

    @inlineCallbacks
    def requestState(self, c=None):
        server = yield self.cxn.get_server(self.servername)
        request = {self.name: None}
        yield server.states(json.dumps(request))
    
    @inlineCallbacks
    def requestCurrent(self, c=None):
        server = yield self.cxn.get_server(self.servername)
        request = {self.name: None}
        yield server.currents(json.dumps(request))
    
    @inlineCallbacks
    def requestPower(self, c=None):
        server = yield self.cxn.get_server(self.servername)
        request = {self.name: None}
        yield server.powers(json.dumps(request))

#    @inlineCallbacks
#    def requestValues(self, c=None):
#        server = yield self.cxn.get_server(self.servername)
#        for parameter in self.update_parameters:
#            yield getattr(server, parameter)()
# 
    def receive_update(self, c, signal_json):
        print 'update', self.i
        self.i += 1
        self.free = False
        signal = json.loads(signal_json)
        for message_type, message in signal.items():
            device_message = message.get(self.name)
            if (message_type == 'states') and (device_message is not None):
                if device_message:
                    self.state_button.setChecked(1)
                    self.state_button.setText('On')
                    self.state = True
                else:
                    self.state_button.setChecked(0)
                    self.state_button.setText('Off')
                    self.state = False
            if (message_type == 'currents') and (device_message is not None):
                self.current_box.setValue(device_message)
            if (message_type == 'powers') and (device_message is not None):
                self.power_box.setValue(device_message * 1e3)
        self.free = True
    
    @inlineCallbacks
    def onNewState(self):
        if self.free:
            server = yield self.cxn.get_server(self.servername)
            request = {self.name: None}
            response = yield server.states(json.dumps(request))
            server_state = json.loads(response)[self.name]
            if server_state == self.state:
                request = {self.name: None}
                if self.state:
                    yield server.shutdown(json.dumps(request))
                else:
                    yield server.warmup(json.dumps(request))

    def onNewCurrent(self):
        if self.free:
            self.hasNewCurrent = True
   
    def onNewPower(self):
        pass

    @inlineCallbacks
    def writeValues(self):
        if self.hasNewCurrent:
            server = yield self.cxn.get_server(self.servername)
            request = {self.name: self.current_box.value()}
            yield server.currents(json.dumps(request))
            self.hasNewCurrent = False

    def enterEvent(self, c):
        self.mouseHover.emit(True)
           
    def reinitialize(self):
        self.setDisabled(False)

    def disable(self):
        self.setDisabled(True)

    @inlineCallbacks
    def closeEvent(self, x):
        server = yield self.cxn.get_server(self.servername)
        yield server.signal__update(self.update_id)
        yield server.removeListener(listener=self.receive_update, source=None, 
                                 ID=self.update_id)
        x.accept()
        self.reactor.stop()

class MultipleClientContainer(QtGui.QWidget):
    def __init__(self, client_list, reactor, cxn=None):
        QtGui.QDialog.__init__(self)
        self.client_list = client_list
        self.reactor = reactor
        self.cxn = cxn
        self.connect()
 
    @inlineCallbacks
    def connect(self):
        if self.cxn is None:
            self.cxn = connection()
            yield self.cxn.connect()
        self.populateGUI()

    def populateGUI(self):
        self.layout = QtGui.QHBoxLayout()
        for client in self.client_list:
            self.layout.addWidget(client)
        self.setFixedSize(210 * len(self.client_list), 140)
        self.setLayout(self.layout)

    def closeEvent(self, x):
        self.reactor.stop()
