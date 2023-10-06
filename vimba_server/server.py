"""
### BEGIN NODE INFO
[info]
name = vimba
version = 1.0
description = 
instancename = %LABRADNODE%_vimba

[startup]
cmdline = python3.9 %FILE%
timeout = 60

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""
import h5py
from labrad.server import LabradServer, setting, Signal
from twisted.internet import reactor
import numpy as np
from vimba import *

class Server(LabradServer):
    """ Provides access to allied vision cameras using vimba """
    name = '%LABRADNODE%_vimba'
    update = Signal(698688, 'signal: update', 's')

    @setting(0)
    def arm_mako1(self, c):
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


    @setting(1, data_path='s')
    def get_frames_mako1(self, c, data_path):
        reactor.callInThread(self._get_frames_mako1, data_path)

    def _get_frames_mako1(self, data_path):
        image = None
        bright = None
        with Vimba.get_instance() as vimba:
            with vimba.get_camera_by_id("DEV_000F315B946B") as cam:
                image = cam.get_frame(timeout_ms=1000000).as_numpy_ndarray()
                bright = cam.get_frame(timeout_ms=1000000).as_numpy_ndarray()
        
        with h5py.File(data_path, "w") as h5f:
            h5f.create_dataset("image", data=np.squeeze(image, -1), compression="gzip", compression_opts=4)
            h5f.create_dataset("bright", data=np.squeeze(bright, -1), compression="gzip", compression_opts=4)

        self.update(data_path)
    
    @setting(2)
    def arm_mako2(self, c):
        with Vimba.get_instance() as vimba:
            with vimba.get_camera_by_id("DEV_000F315B959E") as cam:
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


    @setting(3, data_path='s')
    def get_frames_mako2(self, c, data_path):
        reactor.callInThread(self._get_frames_mako2, data_path)

    def _get_frames_mako2(self, data_path):
        image = None
        bright = None
        with Vimba.get_instance() as vimba:
            with vimba.get_camera_by_id("DEV_000F315B959E") as cam:
                image = cam.get_frame(timeout_ms=1000000).as_numpy_ndarray()
                bright = cam.get_frame(timeout_ms=1000000).as_numpy_ndarray()
                image = np.rot90(image, -1)
                bright = np.rot90(bright, -1)
        
        with h5py.File(data_path, "w") as h5f:
            h5f.create_dataset("image", data=np.squeeze(image, -1), compression="gzip", compression_opts=4)
            h5f.create_dataset("bright", data=np.squeeze(bright, -1), compression="gzip", compression_opts=4)

        self.update(data_path)


if __name__ == "__main__":
    from labrad import util
    util.runServer(Server())
