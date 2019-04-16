import json
import numpy as np

from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks

from client_tools.widgets import ClickableLabel, SuperSpinBox

class RFClient(QtGui.QGroupBox):
    name = None
    DeviceProxy = None
    updateID = np.random.randint(0, 2**31 - 1)
    amplitudeDisplayUnits = [(0, 'dBm')]
    amplitudeDigits = None
    frequencyDisplayUnits = [(-6, 'uHz'), (-3, 'mHz'), (0, 'Hz'), (3, 'kHz'), 
                             (6, 'MHz'), (9, 'GHz')]
    frequencyDigits = None
    spinboxWidth = 100
    
    def __init__(self, reactor, cxn=None):
        QtGui.QDialog.__init__(self)
        self.reactor = reactor
        reactor.callInThread(self.initialize)
        self.connectLabrad()
    
    def initialize(self):
        import labrad
        cxn = labrad.connect(name=self.name)
        self.device = self.DeviceProxy(cxn)
        self.reactor.callFromThread(self.populateGUI)

    def populateGUI(self):
        self.nameLabel = ClickableLabel('<b>' + self.name + '</b>')
        self.stateButton = QtGui.QPushButton()
        self.stateButton.setCheckable(True)
        
        self.frequencyLabel = ClickableLabel('Frequency: ')
        self.frequencyBox = SuperSpinBox(self.device._frequency_range, 
                                          self.frequencyDisplayUnits, 
                                          self.frequencyDigits)
        self.frequencyBox.setFixedWidth(self.spinboxWidth)
        
        self.amplitudeLabel = ClickableLabel('Amplitude: ')
        self.amplitudeBox = SuperSpinBox(self.device._amplitude_range, 
                                          self.amplitudeDisplayUnits, 
                                          self.amplitudeDigits)
        self.amplitudeBox.setFixedWidth(self.spinboxWidth)
        
        self.layout = QtGui.QGridLayout() 
        self.layout.addWidget(self.nameLabel, 0, 0, 1, 1, 
                              QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.stateButton, 0, 1)
        self.layout.addWidget(self.frequencyLabel, 1, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.frequencyBox, 1, 1)
        self.layout.addWidget(self.amplitudeLabel, 2, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.amplitudeBox, 2, 1)
        self.setLayout(self.layout)

        self.setWindowTitle(self.name)
        self.setFixedSize(110 + self.spinboxWidth, 100)
        
        self.connectSignals()
        self.reactor.callInThread(self.getAll)

    def getAll(self):
        self.getState()
        self.getFrequency()
        self.getAmplitude()

    def getState(self):
        state = self.device.state
        self.reactor.callFromThread(self.displayState, state)

    def displayState(self, state):
        if state:
            self.stateButton.setChecked(1)
            self.stateButton.setText('On')
        else:
            self.stateButton.setChecked(0)
            self.stateButton.setText('Off')

    def getFrequency(self):
        frequency = self.device.frequency
        self.reactor.callFromThread(self.displayFrequency, frequency)

    def displayFrequency(self, frequency):
        self.frequencyBox.display(frequency)
    
    def getAmplitude(self):
        amplitude = self.device.amplitude
        self.reactor.callFromThread(self.displayAmplitude, amplitude)

    def displayAmplitude(self, amplitude):
        self.amplitudeBox.display(amplitude)

    def connectSignals(self):
        self.nameLabel.clicked.connect(self.onNameLabelClick)
        self.frequencyLabel.clicked.connect(self.onFrequencyLabelClick)
        self.amplitudeLabel.clicked.connect(self.onAmplitudeLabelClick)
        
        self.stateButton.released.connect(self.onNewState)
        self.frequencyBox.returnPressed.connect(self.onNewFrequency)
        self.amplitudeBox.returnPressed.connect(self.onNewAmplitude)
    
    def onNameLabelClick(self):
        self.reactor.callInThread(self.getAll)
    
    def onFrequencyLabelClick(self):
        self.reactor.callInThread(self.getFrequency)
    
    def onAmplitudeLabelClick(self):
        self.reactor.callInThread(self.getAmplitude)
    
    def onNewState(self):
        state = self.stateButton.isChecked()
        self.reactor.callInThread(self.setState, state)
    
    def setState(self, state):
        self.device.state = state
        self.reactor.callFromThread(self.displayState, state)
        
    def onNewFrequency(self):
        frequency = self.frequencyBox.value()
        self.reactor.callInThread(self.setFrequency, frequency)

    def setFrequency(self, frequency):
        self.device.frequency = frequency
        self.reactor.callFromThread(self.displayFrequency, frequency)
    
    def onNewAmplitude(self):
        amplitude = self.amplitudeBox.value()
        self.reactor.callInThread(self.setAmplitude, amplitude)

    def setAmplitude(self, amplitude):
        self.device.amplitude = amplitude
        self.reactor.callFromThread(self.displayAmplitude, amplitude)
    
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
        state = update.get('state')
        if state is not None:
            self.displayState(state)
        frequency = update.get('frequency')
        if frequency is not None:
            self.displayFrequency(frequency)
        amplitude = update.get('amplitude')
        if amplitude is not None:
            self.displayAmplitude(amplitude)
    
    def closeEvent(self, x):
        self.reactor.stop()

if __name__ == '__main__':
    from rf2.devices import alpha

    class Client(RFClient):
        name = 'alpha'
        frequencyDigits = 6
        amplitudeDigits = 2
        DeviceProxy = alpha.DeviceProxy
    
    from PyQt4 import QtGui
    app = QtGui.QApplication([])
    from client_tools import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor

    widget = Client(reactor)
    widget.show()
    reactor.run()
