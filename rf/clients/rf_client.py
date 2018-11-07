import json
import numpy as np

from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from twisted.internet.defer import inlineCallbacks

from client_tools.connection import connection
from client_tools.widgets import SuperSpinBox

class RFClient(QtGui.QGroupBox):
    update_id = None
    frequency_display_units = None
    frequency_digits = None
    amplitude_display_units = None
    amplitude_digits = None
    offset_display_units = None
    offset_digits = None
    offset_range = None
    
    def __init__(self, reactor, cxn=None):
        QtGui.QDialog.__init__(self)
        self.reactor = reactor
        self.cxn = cxn 
        self.set_defaults()
        self.initialize()

    def set_defaults(self):
        if getattr(self, 'update_id') is None:
            self.update_id = np.random.randint(0, 2**31-1)
        if getattr(self, 'frequency_display_units') is None:
            self.frequency_display_units = [(-6, 'uHz'), (-3, 'mHz'), (0, 'Hz'),
                                            (3, 'kHz'), (6, 'MHz'), (9, 'GHz')]
        if getattr(self, 'frequency_digits') is None:
            self.frequency_digits = 4
        if getattr(self, 'amplitude_display_units') is None:
            self.amplitude_display_units = [(0, '')]
        if getattr(self, 'amplitude_digits') is None:
            self.amplitude_digits = 4        
        if getattr(self, 'offset_display_units') is None:
            self.offset_display_units = [(0, 'V')]
        if getattr(self, 'offset_digits') is None:
            self.offset_digits = 4
        if getattr(self, 'offset_range') is None:
            self.offset_range = [0, 0]

    @inlineCallbacks
    def initialize(self):
        if self.cxn is None:
            self.cxn = connection()
            cname = '{} - {} - client'.format(self.servername, self.name)
            yield self.cxn.connect()
        yield self.initialize_device()
        yield self.get_device_info()
        self.populateGUI()
        yield self.connectSignals()
        yield self.requestValues()

    @inlineCallbacks
    def initialize_device(self):
        server = yield self.cxn.get_server(self.servername)
        request = {self.name: {}}
        yield server.initialize_devices(json.dumps(request))

    @inlineCallbacks
    def get_device_info(self):
        server = yield self.cxn.get_server(self.servername)
        request = {self.name: {}}
        response_json = yield server.get_device_infos(json.dumps(request))
        response = json.loads(response_json)
        for k, v in response[self.name].items():
            setattr(self, k, v)
    
    def populateGUI(self):
        self.state_button = QtGui.QPushButton()
        self.state_button.setCheckable(1)
        
        self.frequency_box = SuperSpinBox(self.frequency_range, 
                                          self.frequency_display_units, 
                                          self.frequency_digits)
        self.frequency_box.setFixedWidth(self.spinbox_width)
        self.frequency_box.display(0)
        
        self.amplitude_box = SuperSpinBox(self.amplitude_range, 
                                          self.amplitude_display_units, 
                                          self.amplitude_digits)
        self.amplitude_box.setFixedWidth(self.spinbox_width)
        self.amplitude_box.display(0)
        
        self.offset_box = SuperSpinBox(self.offset_range, 
            self.offset_display_units, self.offset_digits)
        self.offset_box.setFixedWidth(self.spinbox_width)
        self.offset_box.display(0)


        self.layout = QtGui.QGridLayout() 

        row = 0
        height = 40
        self.layout.addWidget(QtGui.QLabel('<b>'+self.name+'</b>'), 
                              0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        if 'state' in self.update_parameters:
            self.layout.addWidget(self.state_button, 0, 1)
        else:
            self.layout.addWidget(QtGui.QLabel('always on'), 
                                  0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        if 'frequency' in self.update_parameters:
            row += 1
            height += 30
            self.layout.addWidget(QtGui.QLabel('Frequency: '), 
                                  row, 0, 1, 1, QtCore.Qt.AlignRight)
            self.layout.addWidget(self.frequency_box, row, 1)
        if 'amplitude' in self.update_parameters:
            row += 1
            height += 30
            self.layout.addWidget(QtGui.QLabel('Amplitude: '), 
                                  row, 0, 1, 1, QtCore.Qt.AlignRight)
            self.layout.addWidget(self.amplitude_box, row, 1)
        if 'offset' in self.update_parameters:
            row += 1
            height += 30
            self.layout.addWidget(QtGui.QLabel('Offset: '), 
                                  row, 0, 1, 1, QtCore.Qt.AlignRight)
            self.layout.addWidget(self.offset_box, row, 1)


        self.setWindowTitle('{} - {} - client'.format(self.servername, self.name))
        self.setLayout(self.layout)
        self.setFixedSize(100 + self.spinbox_width, height)

    @inlineCallbacks
    def connectSignals(self):
        self.hasNewState = False
        self.hasNewFrequency = False
        self.hasNewAmplitude = False
        self.hasNewOffset = False
        server = yield self.cxn.get_server(self.servername)
        yield server.signal__update(self.update_id)
        yield server.addListener(listener=self.receive_update, source=None, 
                                 ID=self.update_id)
        yield self.cxn.add_on_connect(self.servername, self.reinitialize)
        yield self.cxn.add_on_disconnect(self.servername, self.disable)

        self.state_button.released.connect(self.onNewState)
        self.frequency_box.returnPressed.connect(self.onNewFrequency)
        self.amplitude_box.returnPressed.connect(self.onNewAmplitude)
        self.offset_box.returnPressed.connect(self.onNewOffset)
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.writeValues)
        self.timer.start(self.update_time)

    @inlineCallbacks
    def requestValues(self, c=None):
        server = yield self.cxn.get_server(self.servername)
        for parameter in self.update_parameters:
            if parameter == 'frequency':
                method_name = 'frequencies'
            else:
                method_name = parameter + 's'
            method = getattr(server, method_name)
            request = {self.name: None}
            yield method(json.dumps(request))
 
    def receive_update(self, c, signal_json):
        signal = json.loads(signal_json)
        self.free = False
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
                
            if (message_type == 'frequencies') and (device_message is not None):
                if 'frequency' in self.update_parameters:
                    self.frequency_box.display(device_message)
            if (message_type == 'amplitudes') and (device_message is not None):
                if 'amplitude' in self.update_parameters:
                    self.amplitude_box.display(device_message)
            if (message_type == 'offsets') and (device_message is not None):
                if 'offset' in self.update_parameters:
                    self.offset_box.display(device_message)
        self.free = True
    
    @inlineCallbacks
    def onNewState(self):
        if self.free:
            server = yield self.cxn.get_server(self.servername)
            request = {self.name: None}
            response = yield server.states(json.dumps(request))
            server_state = json.loads(response)[self.name]
            if server_state == self.state:
                request = {self.name: not self.state}
                yield server.states(json.dumps(request))

    def onNewFrequency(self):
        if self.free:
            self.hasNewFrequency = True
   
    def onNewAmplitude(self):
        if self.free:
            self.hasNewAmplitude = True
    
    def onNewOffset(self):
        if self.free:
            self.hasNewOffset = True

    @inlineCallbacks
    def writeValues(self):
        if self.hasNewFrequency:
            self.hasNewFrequency = False
            server = yield self.cxn.get_server(self.servername)
            request = {self.name: self.frequency_box.value()}
            yield server.frequencies(json.dumps(request))
        elif self.hasNewAmplitude:
            self.hasNewAmplitude = False
            server = yield self.cxn.get_server(self.servername)
            request = {self.name: self.amplitude_box.value()}
            yield server.amplitudes(json.dumps(request))
        elif self.hasNewOffset:
            self.hasNewOffset = False
            server = yield self.cxn.get_server(self.servername)
            request = {self.name: self.offset_box.value()}
            yield server.offsets(json.dumps(request))
           
    def reinitialize(self):
        self.setDisabled(False)

    def disable(self):
        self.setDisabled(True)

    def closeEvent(self, x):
        self.reactor.stop()

class MultipleWidgetsContainer(QtGui.QWidget):
    def __init__(self,reactor):
        QtGui.QDialog.__init__(self)
        self.reactor = reactor
        self.initialize()
 
    def initialize(self):
        self.populateGUI()

    def populateGUI(self):
        self.layout = QtGui.QHBoxLayout()
        for WidgetClass in self.widgets:
            widget = WidgetClass(self.reactor)
            self.layout.addWidget(widget)
        self.setFixedSize(220 * len(self.widgets), 120)
        self.setLayout(self.layout)

    def closeEvent(self, x):
        self.reactor.stop()
