import os
import h5py
import json

from device_server.device import DefaultDevice
from andor_server.proxy import AndorSDKProxy

class IKon(DefaultDevice):
    andor_servername = None
    andor_serialnumber = None

    data_directory = os.path.join(os.getenv('PROJECT_DATA_PATH'), 'data')
    compression = 'gzip'
    compression_level = 4

    def initialize(self, config):
        super(IKon, self).initialize(config)
        self.connect_to_labrad()
        
        self.andor_server = self.cxn[self.andor_servername]
        self.andor = AndorSDKProxy(self.andor_server)
    
    def record(self, record_path=None, record_type=None, record_settings={}):
        """ To be implemented by child class """
    
    def _save(self, images, record_path):
        data_path = os.path.join(self.data_directory, record_path + '.hdf5')
        data_directory = os.path.dirname(data_path)
        if not os.path.isdir(data_directory):
            os.makedirs(data_directory)

        h5f = h5py.File(data_path, "w")
        for image in images:
            h5f.create_dataset(image, data=images[image], 
                    compression=self.compression, 
                    compression_opts=self.compression_level)
        h5f.close()

    def _send_update(self, record_path, record_type):
        signal = {
            self.name: {
                'record_path': record_path,
                'record_type': record_type,
                },
            }
        self.server.update(json.dumps(signal))
