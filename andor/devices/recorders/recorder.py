import h5py
import json
import numpy as np
import os
from time import strftime

class Recorder(object):
    config_path = None
    number_kinetics = None
    exposure_time = None
    acquisition_mode = None
    data_directory = os.path.join(os.getenv('PROJECT_DATA_PATH'), 'data')
    compression = None
    compression_level = None

    def __init__(self, config_json='{}'):
        config = json.loads(config_json) 
        for key, value in config.items():
            setattr(self, key, value)

    def record(self, cam, record_name):
        pass
    
    def save(self, images, rel_data_path):
        data_path = os.path.join(self.data_directory, rel_data_path + '.hdf5')
        data_directory = os.path.dirname(data_path)
        if not os.path.isdir(data_directory):
            os.makedirs(data_directory)

        print 'print saving data to {}'.format(data_path)
        h5f = h5py.File(data_path, "w")
        for image in images:
            h5f.create_dataset(image, data=images[image], 
                    compression=self.compression, 
                    compression_opts=self.compression_level)
        h5f.close()

    def send_update(self, device, record_path):
        signal = {
            device.name: {
                'record_path': record_path,
                'record_type': self.name,
                },
            }
        device.device_server.update(json.dumps(signal))
