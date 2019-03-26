import json
import numpy as np
import sys
import time

from PyQt4 import QtGui, QtCore, Qt
from PyQt4.QtCore import pyqtSignal 
from twisted.internet.defer import inlineCallbacks
from twisted.internet import defer

from client_tools.connection import connection

class ParameterLabel(QtGui.QLabel):
    clicked = QtCore.pyqtSignal()
    
    def mousePressEvent(self, x):
        self.clicked.emit()
    

class CurrentControllerClient(QtGui.QGroupBox):
    name = None
    mouseHover = pyqtSignal(bool)
    state = None
#    qt_style = 'Gtk+'
    i = 0
    DeviceProxy = None
    current_stepsize = 0.0001
    
    def __init__(self, reactor):
        QtGui.QDialog.__init__(self)
        self.reactor = reactor
        reactor.callInThread(self.initialize)

    def initialize(self):
        import labrad
        cxn = labrad.connect(name=self.name)
        self.device = self.DeviceProxy(cxn)
        self.reactor.callFromThread(self.populateGUI)
        self.reactor.callFromThread(self.connectSignals)

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
        self.current_box.setRange(*self.device.current_range)
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
    
        self.update_displays()

    def update_displays(self):
        self.reactor.callInThread(self._update_displays) 

    def _update_displays(self, c=None):
        self.get_state()
        self.get_current()
        self.get_power()
    
    def get_state(self):
        self.reactor.callInThread(self._get_state)

    def _get_state(self):
        state = self.device.state
        self.reactor.callFromThread(self.display_state, state)

    def display_state(self, state):
        if state:
            self.state_button.setChecked(1)
            self.state_button.setText('On')
        else:
            self.state_button.setChecked(0)
            self.state_button.setText('Off')
   
    def get_current(self):
        self.reactor.callInThread(self._get_current)

    def _get_current(self):
        current = self.device.current
        self.reactor.callFromThread(self.display_current, current)

    def display_current(self, current):
        self.current_box.setValue(current)
    
    def get_power(self):
        self.reactor.callInThread(self._get_power)
    
    def _get_power(self):
        power = self.device.power
        self.reactor.callFromThread(self.display_power, power)

    def display_power(self, power):
        self.power_box.setValue(power * 1e3)

    def connectSignals(self):
        self.hasNewState = False
        self.hasNewCurrent = False
        self.hasNewPower = False
        
        self.state_button.released.connect(self.onNewState)
        self.current_box.valueChanged.connect(self.onNewCurrent)
        
        self.power_label.clicked.connect(self.update_displays)
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.writeValues)
        self.timer.start(self.update_time)

    def onNewState(self):
        if not self.state_button.isChecked():
            self.reactor.callInThread(self.set_state, False)
            self.display_state(False)
        else:
            self.reactor.callInThread(self.set_state, True)
            self.display_state(True)

    def onNewCurrent(self):
        self.hasNewCurrent = True
   
    def onNewPower(self):
        pass

    def writeValues(self):
        if self.hasNewCurrent:
            current = self.current_box.value()
            self.set_current(current)
            self.hasNewCurrent = False
            time.sleep(0.15)
            self.get_power()

    def set_current(self, current):
        self.reactor.callInThread(self._set_current, current)

    def _set_current(self, current):
        self.device.current = current

    def set_state(self, state):
        self.reactor.callInThread(self._set_state, state)
    
    def _set_state(self, state):
        self.device.state = state

    def enterEvent(self, c):
        self.mouseHover.emit(True)
           
    def reinitialize(self):
        self.setDisabled(False)

    def disable(self):
        self.setDisabled(True)

    def closeEvent(self, x):
        self.reactor.stop()

class MultipleClientContainer(QtGui.QWidget):
    name = None
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
        self.setWindowTitle(self.name)
        self.setLayout(self.layout)

    def closeEvent(self, x):
        self.reactor.stop()

#if __name__ == '__main__':
#    from current_controller3.devices.zs import DeviceProxy as ZSProxy
#
#    class ZSClient(CurrentControllerClient):
#        name = 'zs'
#        update_time = 200
#        DeviceProxy = ZSProxy
#    
#    from PyQt4 import QtGui
#    app = QtGui.QApplication([])
#    from client_tools import qt4reactor 
#    qt4reactor.install()
#    from twisted.internet import reactor
#
#    widget = ZSClient(reactor)
#    widget.show()
#    reactor.run()
#
#
