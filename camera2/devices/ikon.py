import os
import h5py

from andor_server2.proxy import AndorProxy


class IKon(object):
    _andor_serialnumber = None

    _data_directory = os.path.join(os.getenv('PROJECT_DATA_PATH'), 'data')
    _compression = 'gzip'
    _compression_level = 4
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'andor' not in globals():
            global andor
            import andor_server2.andor as andor

    def _setup(self):
        andor.Initialize()
    
    def _save(self, images, record_path):
        data_path = os.path.join(self._data_directory, record_path + '.hdf5')
        data_directory = os.path.dirname(data_path)
        if not os.path.isdir(data_directory):
            os.makedirs(data_directory)

        h5f = h5py.File(data_path, "w")
        for image in images:
            h5f.create_dataset(image, data=images[image], 
                    compression=self._compression, 
                    compression_opts=self._compression_level)
        h5f.close()

class IKonProxy(IKon):
    _andor_servername = None

    def __init__(self, cxn=None, **kwargs):
        if cxn == None:
            import labrad
            cxn = labrad.connect()
        from andor_server.proxy import AndorSDKProxy
        global andor
        andor_server = cxn[self._andor_servername]
        andor = AndorProxy(andor_server)
        IKon.__init__(self, **kwargs)
