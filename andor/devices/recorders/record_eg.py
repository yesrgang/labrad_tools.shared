import h5py
import json
import numpy as np
import os
import time

from recorder import Recorder

class RecordEg(Recorder):
    name = 'record_eg'
    number_kinetics = 1
    exposure_time = 2e-3
    acquisition_mode = 4
    number_sub_frames = 3
    shutter_type = 1
    shutter_mode = 1
    shutter_closing_time = 0
    shutter_opening_time = 0
    trigger_mode = 1
    kinetic_cycle_time = 0
   
    data_directory = os.path.join(os.getenv('PROJECT_DATA_PATH'), 'data')
    compression = 'gzip'
    compression_level = 4

    def record(self, device, record_path):
        if record_path:
            print '!'
            cam = device.cam
            cam.AbortAcquisition()
            cam.SetAcquisitionMode(self.acquisition_mode)
#            cam.SetNumberKinetics(self.number_kinetics)
            cam.SetExposureTime(self.exposure_time)
            cam.SetShutter(self.shutter_type, self.shutter_mode, 
                           self.shutter_closing_time, 
                           self.shutter_opening_time)
            cam.SetTriggerMode(self.trigger_mode)
#            cam.SetKineticCycleTime(self.kinetic_cycle_time)
#            cam.SetImage(1, 1, 1, cam.width, 1, cam.height)

            sub_height = int(cam.height / self.number_sub_frames)
            offset_height = cam.height - sub_height
            cam.SetFastKineticsEx(sub_height, self.number_sub_frames, 
                    self.exposure_time, 4, 1, 1, offset_height)

            cam.StartAcquisition()
            data = []
            cam.GetAcquiredData(data)
            data = np.array(data, dtype=np.uint16)
            data = np.reshape(data, (self.number_sub_frames, sub_height, cam.width))
            images = {key: data[i] for i, key in enumerate(["image_g", "image_e", "bright"])}
            
            cam.StartAcquisition()
            data = []
            cam.GetAcquiredData(data)
            data = np.array(data, dtype=np.uint16)
            data = np.reshape(data, (self.number_sub_frames, sub_height, cam.width))
            background_images = {key: data[i] for i, key in 
                    enumerate(["dark_g", "dark_e", "dark_bright"])}

            images.update(background_images)
            
            self.save(images, record_path)
            self.send_update(device, record_path)
            
#import json
#import numpy as np
#import h5py
#from time import strftime
#
#from recorder import Recorder
#
#class RecordEg(Recorder):
#    name = 'record_eg'
#    config_path = './devices/recorders/record_eg.json'
#
#    def record(self, device, record_path):
#        if record_path:
#            cam = device.cam
#            cam.AbortAcquisition()
#            cam.SetShutter(1, 1, 0, 0)
#
#            cam.SetAcquisitionMode(self.acquisition_mode)
#
#            sub_height = int(cam.height / self.number_sub_frames)
#            offset_height = cam.height - sub_height
#            cam.SetFastKineticsEx(sub_height, self.number_sub_frames, 
#                    self.exposure_time, 4, 1, 1, offset_height)
#
#            cam.StartAcquisition()
#            data = []
#            cam.GetAcquiredData(data)
#            data = np.array(data, dtype=np.uint16)
#            data = np.reshape(data, (self.number_sub_frames, sub_height, cam.width))
#            images = {key: data[i] for i, key in enumerate(["image_g", "image_e", "bright"])}
#            
#            cam.StartAcquisition()
#            data = []
#            cam.GetAcquiredData(data)
#            data = np.array(data, dtype=np.uint16)
#            data = np.reshape(data, (self.number_sub_frames, sub_height, cam.width))
#            background_images = {key: data[i] for i, key in 
#                    enumerate(["dark_g", "dark_e", "dark_bright"])}
#
#            images.update(background_images)
#            
#            self.save(images, record_path)
#            self.send_update(device, record_path)
