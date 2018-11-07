from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.reactor import callInThread

from andor.devices.lib.andor import Andor
from andor.devices.lib.helpers import import_recorder, import_processor
from device_server.old_server import Device

class Ikon(Device):
    # 0 = high, 1 = low, 2 = off
    fan_mode = 2

    # min is -80
    temperature = -70

    # ?, set to 0
    cooler_mode = 0
    
    # 1 = on, 0 = off
    cooler_on = 1
    
    # ?, set to 4 for image
    read_mode = 4
    
    # ?, set to 1
    shutter_type = 1
    
    # ?, set to 0
    shutter_mode = 0
    
    shutter_closing_time = 0
    shutter_opening_time = 0
    
    # 1 = external, 0 = internal
    trigger_mode = 1
    
    accumulation_cycle_time = 0
    number_accumulations = 1
    kinetic_cycle_time = 0
    pre_amp_gain = 0
    hs_speed_type = 0
    hs_speed_index = 0
    vs_speed_index = 1

    @inlineCallbacks
    def initialize(self):
        yield
        self.cam = Andor()
        self.cam.SetFanMode(self.fan_mode)
        self.cam.SetTemperature(self.temperature)
        self.cam.SetCoolerMode(self.cooler_mode)
        if self.cooler_on:
            self.cam.CoolerON()
        else:
            self.cam.CoolerOFF()
        self.cam.SetReadMode(self.read_mode)
        self.cam.SetShutter(self.shutter_type, self.shutter_mode, 
                            self.shutter_closing_time, 
                            self.shutter_opening_time)
        self.cam.SetTriggerMode(self.trigger_mode)
        self.cam.SetAccumulationCycleTime(self.accumulation_cycle_time)
        self.cam.SetNumberAccumulations(self.number_accumulations)
        self.cam.SetKineticCycleTime(self.kinetic_cycle_time)
        self.cam.SetPreAmpGain(self.pre_amp_gain)
        self.cam.SetHSSpeed(self.hs_speed_type, self.hs_speed_index)
        self.cam.SetVSSpeed(self.vs_speed_index)
        return

    def record(self, record_path='', record_type='', recorder_config='{}'):
        if record_path and record_type:
            Recorder = import_recorder(record_type)
            recorder = Recorder(recorder_config)
            callInThread(recorder.record, self, record_path)

    def process(self, settings):
        processor_type = settings.get('processor_type')
        if processor_type:
            Processor = import_processor(processor_type)
            processor = Processor(settings)
            return processor.get_counts()


__device__ = Ikon
