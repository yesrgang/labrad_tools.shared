import numpy as np
from vimba import *

with Vimba.get_instance() as vimba:
    with vimba.get_camera_by_id("DEV_000F315B946B") as cam:
        cam.GVSPAdjustPacketSize.run()
        while not cam.GVSPAdjustPacketSize.is_done():
            pass

        cam.TriggerSelector.set("FrameStart")
        cam.TriggerSource.set('Line1')
        cam.TriggerActivation.set("RisingEdge")
        cam.TriggerMode.set("On")
        
        cam.ExposureMode.set("Timed")
        cam.ExposureTimeAbs.set(1000) # [us]
        
        cam.Gain.set(0)

        cam.AcquisitionMode.set('SingleFrame')

        print(1)
        image = cam.get_frame(timeout_ms=10000).as_numpy_ndarray()
        print(2)

#image = None
#bright = None
#with Vimba.get_instance() as vimba:
#    with vimba.get_camera_by_id("DEV_000F315B946B") as cam:
#        print(1)
#        print(2)
##        bright = cam.get_frame(timeout_ms=1000000).as_numpy_ndarray()
