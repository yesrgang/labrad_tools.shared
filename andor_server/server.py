"""
### BEGIN NODE INFO
[info]
name = andor2
version = 1.0
description = 
instancename = %LABRADNODE%_andor2

[startup]
cmdline = %PYTHON% %FILE%
timeout = 60

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""
from labrad.server import setting

from andor_server.andor import AndorSDK
from server_tools.threaded_server import ThreadedServer

class AndorServer(ThreadedServer):
    """ Provides access to andor camera using pyandor """
    name = '%LABRADNODE%_andor2'
    cam = None

    def initServer(self):
        self.cam = AndorSDK()
        self.cam.Initialize()
        super(AndorServer, self).initServer()
    
    def stopServer(self):
        self.cam.ShutDown()
        super(AndorServer, self).stopServer()

    def _get_cam(self, serial):
        return self.cam

    @setting(10, serial='i', returns='i')
    def abort_acquisition(self, c, serial):
        cam = self._get_cam(serial)
        cam.AbortAcquisition()
        error_code = cam.error['AbortAcquisition']
        return error_code

    @setting(11, serial='i', returns='i')
    def cancel_wait(self, c, serial):
        cam = self._get_cam(serial)
        cam.CancelWait()
        error_code = cam.error['CancelWait']
        return error_code

    @setting(12, serial='i', returns='i')
    def cooler_off(self, c, serial):
        cam = self._get_cam(serial)
        cam.CoolerOFF()
        error_code = cam.error['CoolerOFF']
        return error_code

    @setting(13, serial='i', returns='i')
    def cooler_on(self, c, serial):
        cam = self._get_cam(serial)
        cam.CoolerON()
        error_code = cam.error['CoolerON']
        return error_code

    @setting(14, serial='i', size='i', returns='i*i')
    def get_acquired_data(self, c, serial, size):
        cam = self._get_cam(serial)
        arr = cam.GetAcquiredData(size)
        error_code = cam.error['GetAcquiredData']
        return error_code, arr
    
    @setting(15, serial='i', size='i', returns='i*i')
    def get_acquired_data_16(self, c, serial, size):
        cam = self._get_cam(serial)
        arr = cam.GetAcquiredData16(size)
        error_code = cam.error['GetAcquiredData16']
        return error_code, arr

    @setting(16, serial='i', returns='iii')
    def get_acquisition_progress(self, c, serial):
        cam = self._get_cam(serial)
        acc, series = cam.GetAcquisitionProgress()
        error_code = cam.error['GetAcquisitionProgress']
        return error_code, acc, series

    @setting(17, serial='i', returns='iiii')
    def get_acquisition_timings(self, c, serial):
        cam = self._get_cam(serial)
        exposure, accumulate, kinetic = cam.GetAcquisitionTimings()
        error_code = cam.error['GetAcquisitionTimings']
        return error_code, exposure, accumulate, kinetic

    @setting(18, serial='i', returns='ii')
    def get_available_cameras(self, c, serial):
        cam = self._get_cam(serial)
        totalCameras = cam.GetAvailableCameras()
        error_code = cam.error['GetAvailableCameras']
        return error_code, totalCameras

    @setting(19, serial='i', channel='i', returns='ii')
    def get_bit_depth(self, c, serial, channel):
        cam = self._get_cam(serial)
        depth = cam.GetBitDepth(channel)
        error_code = cam.error['GetBitDepth']
        return error_code, depth

    @setting(20, serial='i', cameraIndex='i', returns='ii')
    def get_camera_handle(self, c, serial, cameraIndex):
        cam = self._get_cam(serial)
        cameraHandle = cam.GetCameraHandle(cameraIndex)
        error_code = cam.error['GetCameraHandle']
        return error_code, cameraHandle

    @setting(21, serial='i', returns='ii')
    def get_camera_serial_number(self, c, serial):
        cam = self._get_cam(serial)
        number = cam.GetCameraSerialNumber()
        error_code = cam.error['GetCameraSerialNumber']
        return error_code, number

    @setting(22, serial='i', returns='ii')
    def get_current_camera(self, c, serial):
        cam = self._get_cam(serial)
        cameraHandle = cam.GetCurrentCamera()
        error_code = cam.error['GetCurrentCamera']
        return error_code, cameraHandle

    @setting(23, serial='i', returns='iii')
    def get_detector(self, c, serial):
        cam = self._get_cam(serial)
        xpixels, ypixels = cam.GetDetector()
        error_code = cam.error['GetDetector']
        return error_code, xpixels, ypixels

    @setting(24, serial='i', returns='ii')
    def get_emccd_gain(self, c, serial):
        cam = self._get_cam(serial)
        gain = cam.GetEMCCDGain()
        error_code = cam.error['GetEMCCDGain']
        return error_code, gain

    @setting(25, serial='i', returns='iii')
    def get_em_gain_range(self, c, serial):
        cam = self._get_cam(serial)
        low, high = cam.GetEMGainRange()
        error_code = cam.error['GetEmGainRange']
        return error_code, low, high

    @setting(26, serial='i', returns='iiv')
    def get_fastest_recommended_vs_speed(self, c, serial):
        cam = self._get_cam(serial)
        index, speed = cam.GetFastestRecommendedVSSpeed()
        error_code = cam.error['GetFastestRecommendedVSSpeed']
        return error_code, index, speed

    @setting(27, serial='i', channel='i', typ='i', index='i', returns='iv')
    def get_hs_speed(self, c, serial, channel, typ, index):
        cam = self._get_cam(serial)
        speed = cam.GetHSSpeed(channel, typ, index)
        error_code = cam.error['GetHSSpeed']
        return error_code, speed

    @setting(28, serial='i', returns='ii')
    def get_number_ad_channels(self, c, serial):
        cam = self.get_cam(serial)
        channels = cam.GetNumberADChannels()
        error_code = cam.error['GetNumberADChannels']
        return error_code, channels

    @setting(29, serial='i', channel='i', typ='i', returns='ii')
    def get_number_hs_speeds(self, c, serial, channel, typ):
        cam = self._get_cam(serial)
        speeds = cam.GetNumberHSSpeeds(channel, typ)
        error_code = cam.error['GetNumberHSSpeeds']
        return error_code, speeds

    @setting(30, serial='i', returns='ii')
    def get_number_pre_amp_gains(self, c, serial):
        cam = self._get_cam(serial)
        noGains = cam.GetNumberPreAmpGains()
        error_code = cam.error['GetNumberPreAmpGains']
        return error_code, noGains

    @setting(31, serial='i', returns='ii')
    def get_number_vs_speeds(self, c, serial):
        cam = self._get_cam(serial)
        speeds = cam.GetNumberVSSpeeds()
        error_code = cam.error['GetNumberVSSpeeds']
        return error_code, speeds

    @setting(32, serial='i', index='i', returns='ii')
    def get_pre_amp_gain(self, c, serial, index):
        cam = self._get_cam(serial)
        gain = cam.GetPreAmpGain(index)
        error_code = cam.error['GetPreAmpGain']
        return error_code, gain

    @setting(33, serial='i', returns='is')
    def get_status(self, c, serial):
        cam = self._get_cam(serial)
        status = cam.GetStatus()
        error_code = cam.error['GetStatus']
        return error_code, status

    @setting(34, serial='i', returns='ii')
    def get_temperature(self, c, serial):
        cam = self._get_cam(serial)
        temperature = cam.GetTemperature()
        error_code = cam.error['GetTemperature']
        return error_code, temperature

    @setting(35, serial='i', index='i', returns='iv')
    def get_vs_speed(self, c, serial, index):
        cam = self._get_cam(serial)
        speed = cam.GetVSSpeed(index)
        error_code = cam.error['GetVSSpeed']
        return error_code, speed

    @setting(36, serial='i', returns='is')
    def initialize(self, c, serial):
        cam = self._get_cam(serial)
        initdir = cam.Initialize()
        error_code = cam.error['Initialize']
        return error_code, initdir

    @setting(37, serial='i', returns='ii')
    def is_cooler_on(self, c, serial):
        cam = self._get_cam(serial)
        iCoolerStatus = cam.IsCoolerOn()
        error_code = cam.error['IsCoolerOn']
        return error_code, iCoolerStatus

    @setting(38, serial='i', time='v', returns='i')
    def set_accumulation_cycle_time(self, c, serial, time):
        cam = self._get_cam(serial)
        cam.SetAccumulationCycleTime(time)
        error_code = cam.error['SetAccumulationCycleTime']
        return error_code

    @setting(39, serial='i', mode='i', returns='i')
    def set_acquisition_mode(self, c, serial, mode):
        cam = self._get_cam(serial)
        cam.SetAcquisitionMode(mode)
        error_code = cam.error['SetAcquisitionMode']
        return error_code

    @setting(40, serial='i', channel='i', returns='i')
    def set_ad_channel(self, c, serial, channel):
        cam = self._get_cam(serial)
        cam.SetADChannel(channel)
        error_code = cam.error['SetADChannel']
        return error_code

    @setting(41, serial='i', mode='i', returns='i')
    def set_cooler_mode(self, c, serial, mode):
        cam = self._get_cam(serial)
        cam.SetCoolerMode(mode)
        error_code = cam.error['SetCoolerMode']
        return error_code

    @setting(42, serial='i', cameraHandle='i', returns='i')
    def set_current_camera(self, c, serial, cameraHandle):
        cam = self._get_cam(serial)
        cam.SetCurrentCamera(cameraHandle)
        error_code = cam.error['SetCurrentCamera']
        return error_code

    @setting(43, serial='i', gainAdvanced='i', returns='i')
    def set_em_advanced(self, c, serial, gainAdvanced):
        cam = self._get_cam(serial)
        cam.SetEMAdvanced(gainAdvanced)
        error_code = cam.error['SetEMAdvanced']
        return error_code

    @setting(44, serial='i', gain='i', returns='i')
    def set_emccd_gain(self, c, serial, gain):
        cam = self._get_cam(serial)
        cam.SetEMCCDGain(gain)
        error_code = cam.error['SetEMCCDGain']
        return error_code

    @setting(45, serial='i', mode='i', returns='i')
    def set_em_gain_mode(self, c, serial, mode):
        cam = self._get_cam(serial)
        cam.SetEMGainMode(mode)
        error_code = cam.error['SetEMGainMode']
        return error_code

    @setting(46, serial='i', time='v', returns='i')
    def set_exposure_time(self, c, serial, time):
        cam = self._get_cam(serial)
        cam.SetExposureTime(time)
        error_code = cam.error['SetExposureTime']
        return error_code

    @setting(47, serial='i', mode='i', returns='i')
    def set_fan_mode(self, c, serial, mode):
        cam = self._get_cam(serial)
        cam.SetFanMode(mode)
        error_code = cam.error['SetFanMode']
        return error_code

    @setting(48, serial='i', exposedRows='i', seriesLength='i', time='v', 
             mode='i', hbin='i', vbin='i', offset='i', returns='i')
    def set_fast_kinetics_ex(self, c, serial, exposedRows, seriesLength, time,
                             mode, hbin, vbin, offset):
        cam = self._get_cam(serial)
        cam.SetFastKineticsEx(exposedRows, seriesLength, time, mode, hbin, vbin,
                              offset)
        error_code = cam.Error['SetFastKineticsEx']
        return error_code

    @setting(49, serial='i', mode='i', returns='i')
    def set_frame_transfer_mode(self, c, serial, mode):
        cam = self._get_cam(serial)
        cam.SetFrameTransferMode(mode)
        error_code = cam.error['SetFrameTransferMode']
        return error_code

    @setting(50, serial='i', typ='i', index='i', returns='i')
    def set_hs_speed(self, c, serial, typ, index):
        cam = self._get_cam(serial)
        cam.SetHSSpeed(typ, index)
        error_code = cam.error['SetHSSpeed']
        return error_code

    @setting(51, serial='i', hbin='i', vbin='i', hstart='i', hend='i', 
             vstart='i', vend='i', returns='i')
    def set_image(self, c, serial, hbin, vbin, hstart, hend, vstart, vend):
        cam = selkkjjjkjkjkf._get_cam(serial)
        cam.SetImage(hbin, vbin, hstart, hend, vstart, vend)
        error_code = cam.error['SetImage']
        return error_code

    @setting(52, serial='i', iHFlip='i', iVFlip='i', returns='i')
    def set_image_flip(self, c, serial, iHFlip, iVFlip):
        cam = self._get_cam(serial)
        cam.SetImageFlip(iHFlip, iVFlip)
        error_code = cam.error['SetImageFlip']
        return error_code

    @setting(53, serial='i', iRotate='i', returns='i')
    def set_image_rotate(self, c, serial, iRotate):
        cam = self._get_cam(serial)
        cam.SetImageRotate(iRotate)
        error_code = cam.error['SetImageRotate']
        return error_code

    @setting(54, serial='i', time='v', returns='i')
    def set_kinetic_cycle_time(self, c, serial, time):
        cam = self._get_cam(serial)
        cam.SetKineticCycleTime(time)
        error_code = cam.error['SetKineticCycleTime']
        return error_code

    @setting(55, serial='i', number='i', returns='i')
    def set_number_accumulations(self, c, serial, number):
        cam = self._get_cam(serial)
        cam.SetNumberAccumulations(number)
        error_code = cam.error['SetNumberAccumulations']
        return error_code

    @setting(56, serial='i', number='i', returns='i')
    def set_number_kinetics(self, c, serial, number):
        cam = self._get_cam(serial)
        cam.SetNumberKinetics(number)
        error_code = cam.error['SetNumberKinetics']
        return error_code

    @setting(57, serial='i', index='i', returns='i')
    def set_output_amplifier(self, c, serial, index):
        cam = self._get_cam(serial)
        cam.SetOutputAmplifier(index)
        error_code = cam.error['SetOutputAmplifier']
        return error_code

    @setting(58, serial='i', index='i', returns='i')
    def set_pre_amp_gain(self, c, serial, index):
        cam = self._get_cam(serial)
        cam.SetPreAmpGain(index)
        error_code = cam.error['SetPreAmpGain']
        return error_code

    @setting(59, serial='i', mode='i', returns='i')
    def set_read_mode(self, c, serial, mode):
        cam = self._get_cam(serial)
        cam.SetReadMode(mode)
        error_code = cam.error['SetReadMode']
        return error_code

    @setting(60, serial='i', typ='i', mode='i', closingtime='i', 
             openingtime='i', returns='i')
    def set_shutter(self, c, serial, typ, mode, closingtime, openingtime):
        cam = self._get_cam(serial)
        cam.SetShutter(typ, mode, closingtime, openingtime)
        error_code = cam.error['SetShutter']
        return error_code

    @setting(61, serial='i', typ='i', mode='i', closingtime='i', 
             openingtime='i', extmode='i')
    def set_shutter_ex(self, c, serial, typ, mode, closingtime, openingtime, 
                       extmode):
        cam = self._get_cam(serial)
        cam.SetShutterEx(typ, mode, closingtime, openingtime, extmode)
        error_code = cam.error['SetShutterEx']
        return error_code

    @setting(62, serial='i', temperature='i', returns='i')
    def set_temperature(self, c, serial, temperature):
        cam = self._get_cam(serial)
        cam.SetTemperature(temperature)
        error_code = cam.error['SetTemperature']
        return error_code

    @setting(63, serial='i', mode='i', returns='i')
    def set_trigger_mode(self, c, serial, mode):
        cam = self._get_cam(serial)
        cam.SetTriggerMode(mode)
        error_code = cam.error['SetTriggerMode']
        return error_code

    @setting(64, serial='i', index='i', returns='i')
    def set_vs_speed(self, c, serial, index):
        cam = self._get_cam(serial)
        cam.SetVSSpeed(index)
        error_code = cam.error['SetVSSpeed']
        return error_code

    @setting(65, serial='i', returns='i')
    def shut_down(self, c, serial):
        cam = self._get_cam(serial)
        cam.ShutDown()
        error_code = cam.error['ShutDown']
        return error_code

    @setting(66, serial='i', returns='i')
    def start_acquisition(self, c, serial):
        cam = self._get_cam(serial)
        cam.StartAcquisition()
        error_code = cam.error['StartAcquisition']
        return error_code

    @setting(67, serial='i', returns='i')
    def wait_for_acquisition(self, c, serial):
        cam = self._get_cam(serial)
        cam.WaitForAcquisition()
        error_code = cam.error['WaitForAcquisition']
        return error_code


Server = AndorServer

if __name__ == "__main__":
    from labrad import util
    util.runServer(Server())
