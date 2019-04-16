from PyQt4 import QtGui, QtCore

from client_tools.widgets import SuperSpinBox, ClickableLabel

class ECDLClient(QtGui.QGroupBox):
    name = None
    DeviceProxy = None

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

    def populateGUI(self):
        self.nameLabel = ClickableLabel('<b>' + self.name + '</b>')
        self.stateButton = QtGui.QPushButton()
        self.stateButton.setCheckable(1)
        
        self.piezoVoltageLabel = ClickableLabel('Piezo Voltage: ')
        self.piezoVoltageBox = SuperSpinBox(self.device._piezo_voltage_range,
                                            self.piezoVoltageDisplayUnits, 
                                            self.piezoVoltageDigits)
        self.piezoVoltageBox.setFixedWidth(self.spinboxWidth)
        self.piezoVoltageBox.display(0)
        
        self.diodeCurrentLabel = ClickableLabel('Diode Current: ')
        self.diodeCurrentBox = SuperSpinBox(self.device._diode_current_range, 
                                            self.diodeCurrentDisplayUnits, 
                                            self.diodeCurrentDigits)
        self.diodeCurrentBox.setFixedWidth(self.spinboxWidth)
        self.diodeCurrentBox.display(0)

        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(self.nameLabel, 0, 0, 1, 1, 
                              QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.stateButton, 0, 1)
        self.layout.addWidget(self.piezoVoltageLabel, 1, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.piezoVoltageBox, 1, 1)
        self.layout.addWidget(self.diodeCurrentLabel, 2, 0, 1, 1, 
                              QtCore.Qt.AlignRight)
        self.layout.addWidget(self.diodeCurrentBox, 2, 1)
        self.setLayout(self.layout)

        self.setWindowTitle(self.name)
        self.setFixedSize(120 + self.spinboxWidth, 100)
        
        self.reactor.callInThread(self.getAll)

    def getAll(self):
        self.getState()
        self.getPiezoVoltage()
        self.getDiodeCurrent()

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

    def getPiezoVoltage(self):
        piezoVoltage = self.device.piezo_voltage
        self.reactor.callFromThread(self.displayPiezoVoltage, piezoVoltage)

    def displayPiezoVoltage(self, piezoVoltage):
        self.piezoVoltageBox.display(piezoVoltage)
    
    def getDiodeCurrent(self):
        diodeCurrent = self.device.diode_current
        self.reactor.callFromThread(self.displayDiodeCurrent, diodeCurrent)

    def displayDiodeCurrent(self, diodeCurrent):
        self.diodeCurrentBox.display(diodeCurrent)

    def callInThread(self, callable, *args, **kwargs):
        def f():
            return self.reactor.callInThread(callable, *args, **kwargs)
        return f

    def connectSignals(self):
        self.hasNewState = False
        self.hasNewPiezoVoltage = False
        self.hasNewDiodeCurrent = False

        self.stateButton.released.connect(self.onNewState)
        self.piezoVoltageBox.returnPressed.connect(self.onNewPiezoVoltage)
        self.diodeCurrentBox.returnPressed.connect(self.onNewDiodeCurrent)
        
        self.nameLabel.clicked.connect(self.callInThread(self.getAll))
        self.piezoVoltageLabel.clicked.connect(self.callInThread(self.getPiezoVoltage))
        self.diodeCurrentLabel.clicked.connect(self.callInThread(self.getDiodeCurrent))
        
    def onNewState(self):
        state = self.stateButton.isChecked()
        self.reactor.callInThread(self.setState, state)

    def onNewPiezoVoltage(self):
        piezoVoltage = self.piezoVoltageBox.value()
        self.reactor.callInThread(self.setPiezoVoltage, piezoVoltage)
    
    def onNewDiodeCurrent(self):
        diodeCurrent = self.diodeCurrentBox.value()
        self.reactor.callInThread(self.setDiodeCurrent, diodeCurrent)

    def setState(self, state):
        self.device.state = state
        self.reactor.callFromThread(self.displayState, state)
    
    def setPiezoVoltage(self, piezoVoltage):
        self.device.piezo_voltage = piezoVoltage
        self.reactor.callFromThread(self.displayPiezoVoltage, piezoVoltage)
    
    def setDiodeCurrent(self, diodeCurrent):
        self.device.diode_current = diodeCurrent
        self.reactor.callFromThread(self.displayDiodeCurrent, diodeCurrent)
   
    def closeEvent(self, x):
        self.reactor.stop()
