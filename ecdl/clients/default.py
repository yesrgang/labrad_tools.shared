import json
import numpy as np
import sys

from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal
from twisted.internet.defer import inlineCallbacks

from client_tools.connection import connection
from client_tools.widgets import SuperSpinBox

class ParameterLabel(QtGui.QLabel):
    clicked = pyqtSignal()
    def mousePressEvent(self, x):
        self.clicked.emit()

class ECDLClient(QtGui.QGroupBox):
    def __init__(self, reactor, cxn=None):
        QtGui.QDialog.__init__(self)
        self.reactor = reactor
        self.cxn = cxn 
        self.connect()

    @inlineCallbacks
    def connect(self):
        if self.cxn is None:
            self.cxn = connection()
            cname = '{} - {} - client'.format(self.servername, self.name)
            yield self.cxn.connect(name=cname)
        yield self.select_device()
        self.populateGUI()
        yield self.connectSignals()
        yield self.requestValues()

    @inlineCallbacks
    def select_device(self):
        server = yield self.cxn.get_server(self.servername)
        request = {self.name: {}}
        yield server.initialize_devices(json.dumps(request))
        request = {self.name: None}
        info_json = yield server.get_device_infos(json.dumps(request))
        info = json.loads(info_json)
        for key, value in info[self.name].items():
            setattr(self, key, value)
    
    def populateGUI(self):
        self.state_button = QtGui.QPushButton()
        self.state_button.setCheckable(1)
        
        self.piezo_voltage_box = SuperSpinBox(self.piezo_voltage_range, 
                                          self.piezo_voltage_display_units, 
                                          self.piezo_voltage_digits)
        self.piezo_voltage_box.setFixedWidth(self.spinbox_width)
        self.piezo_voltage_box.display(0)
        
        self.diode_current_box = SuperSpinBox(self.diode_current_range, 
                                          self.diode_current_display_units, 
                                          self.diode_current_digits)
        self.diode_current_box.setFixedWidth(self.spinbox_width)
        self.diode_current_box.display(0)

        self.layout = QtGui.QGridLayout()
        
        row = 0
        self.layout.addWidget(QtGui.QLabel('<b>'+self.name+'</b>'), 
                              0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        if 'state' in self.update_parameters:
            self.layout.addWidget(self.state_button, 0, 1)
        else:
            self.layout.addWidget(QtGui.QLabel('always on'), 
                                  0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        if 'piezo_voltage' in self.update_parameters:
            row += 1
            self.piezo_voltage_label = ParameterLabel('Piezo Voltage: ')
            self.layout.addWidget(self.piezo_voltage_label, 
                                  row, 0, 1, 1, QtCore.Qt.AlignRight)
            self.layout.addWidget(self.piezo_voltage_box, row, 1)
        if 'diode_current' in self.update_parameters:
            row += 1
            self.diode_current_label = ParameterLabel('Diode Current: ')
            self.layout.addWidget(self.diode_current_label, 
                                  row, 0, 1, 1, QtCore.Qt.AlignRight)
            self.layout.addWidget(self.diode_current_box, row, 1)

        self.setWindowTitle(self.name)
        self.setLayout(self.layout)
        self.setFixedSize(120 + self.spinbox_width, 100)

    @inlineCallbacks
    def connectSignals(self):
        self.hasNewState = False
        self.hasNewPiezoVoltage = False
        self.hasNewDiodeCurrent = False
        server = yield self.cxn.get_server(self.servername)
        yield server.signal__update(self.update_id)
        yield server.addListener(listener=self.receive_update, source=None, 
                                 ID=self.update_id)
        yield self.cxn.add_on_connect(self.servername, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.servername, self.disable)

        self.state_button.released.connect(self.onNewState)
        self.piezo_voltage_box.returnPressed.connect(self.onNewPiezoVoltage)
        self.diode_current_box.returnPressed.connect(self.onNewDiodeCurrent)

        if 'piezo_voltage' in self.update_parameters:
            self.piezo_voltage_label.clicked.connect(self.requestValues)
        if 'diode_current' in self.update_parameters:
            self.diode_current_label.clicked.connect(self.requestValues)
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.writeValues)
        self.timer.start(self.update_time)

    @inlineCallbacks
    def requestValues(self, c=None):
        server = yield self.cxn.get_server(self.servername)
        request = {self.name: None}
        for parameter in self.update_parameters:
            yield getattr(server, parameter + 's')(json.dumps(request))
 
    def receive_update(self, c, signal_json):
        signal = json.loads(signal_json)
        for message_type, message in signal.items():
            device_message = message.get(self.name)
            if (message_type == 'states') and (device_message is not None):
                self.free = False
                if device_message:
                    self.state_button.setChecked(1)
                    self.state_button.setText('On')
                else:
                    self.state_button.setChecked(0)
                    self.state_button.setText('Off')
                self.free = True
            if (message_type == 'piezo_voltages') and (device_message is not None):
                self.free = False
                self.piezo_voltage_box.display(device_message)
                self.free = True
            if (message_type == 'diode_currents') and (device_message is not None):
                self.free = False
                self.diode_current_box.display(device_message)
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

    def onNewPiezoVoltage(self):
        if self.free:
            self.hasNewPiezoVoltage = True
   
    def onNewDiodeCurrent(self):
        if self.free:
            self.hasNewDiodeCurrent = True

    @inlineCallbacks
    def writeValues(self):
        if self.hasNewPiezoVoltage:
            server = yield self.cxn.get_server(self.servername)
            request = {self.name: self.piezo_voltage_box.value()}
            yield server.piezo_voltages(json.dumps(request))
            self.hasNewPiezoVoltage = False
        elif self.hasNewDiodeCurrent:
            server = yield self.cxn.get_server(self.servername)
            request = {self.name: self.diode_current_box.value()}
            yield server.diode_currents(json.dumps(request))
            self.hasNewDiodeCurrent = False
           
    def reinitialize(self):
        self.setDisabled(False)

    def disable(self):
        self.setDisabled(True)

    def closeEvent(self, x):
        self.reactor.stop()

