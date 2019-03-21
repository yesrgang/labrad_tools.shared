from andor2.sdk import AndorSDK

cam = AndorSDK()
cam.Initialize()
cam.SetFanMode(2)
cam.SetTemperature(-70)
cam.SetCoolerMode(0)
cam.CoolerON()

cam.SetReadMode(4)
cam.SetShutter(1, 1, 0, 0)
cam.SetTriggerMode(1)
cam.SetAccumulationCycleTime(0)
cam.SetNumberAccumulations(1)
cam.SetKineticCycleTime(0)
cam.SetPreAmpGain(0)
cam.SetHSSpeed(0, 0)
cam.SetVSSpeed(1)

## for g imaging
#cam.SetNumberKinetics(3)
#cam.SetExposureTime(10e-6)
#cam.SetAcquisitionMode(3)
#cam.SetImage(1, 1, 1, 1024, 1, 1024)

# for eg imaging
cam.SetAcquisitionMode(4)
cam.SetFastKineticsEx(341, 3, 10e-6, 4, 1, 1, 342)
