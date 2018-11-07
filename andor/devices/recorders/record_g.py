import h5py
import json
import numpy as np
import os
import time

from recorder import Recorder

class RecordG(Recorder):
    name = 'record_g'
    number_kinetics = 3
    exposure_time = 10e-6
    acquisition_mode = 3
    shutter_type = 1
    shutter_mode = 1
    shutter_closing_time = 0
    shutter_opening_time = 0
    trigger_mode = 1
    kinetic_cycle_time = 0
   
    data_directory = os.path.join(os.getenv('PROJECT_DATA_PATH'), 'data')
    compression = 'gzip'
    compression_level = 4
    


    def record(self, device, record_name):
        if record_name:
            cam = device.cam
            cam.AbortAcquisition()
            cam.SetNumberKinetics(self.number_kinetics)
            cam.SetExposureTime(self.exposure_time)
            cam.SetAcquisitionMode(self.acquisition_mode)
            cam.SetShutter(self.shutter_type, self.shutter_mode, 
                           self.shutter_closing_time, 
                           self.shutter_opening_time)
            cam.SetTriggerMode(self.trigger_mode)
            cam.SetKineticCycleTime(self.kinetic_cycle_time)
            cam.SetImage(1, 1, 1, cam.width, 1, cam.height)

            print 'starting acquisition' 
            ti = time.time()
            cam.StartAcquisition()
            print '1', time.time() - ti
            ti = time.time()
            cam.StartAcquisition()
            print '2', time.time() - ti
            ti = time.time()
            cam.StartAcquisition()
            print '3', time.time() - ti
            
            data = []
            cam.GetAcquiredData(data)
            data = np.array(data, dtype=np.uint16)
            data = np.reshape(data, (self.number_kinetics, cam.height, cam.width))
            images = {key: data[i] for i, key in enumerate(["image", "bright", "dark"])}
            
            self.save(images, record_name)
            self.send_update(device, record_name)
