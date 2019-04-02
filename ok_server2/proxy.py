class OKProxy(object):
    def __init__(self, server):
        self._server = server

    def okCFrontPanel(self):
        """ This class is the workhorse of the FrontPanel API. 
        
        It's methods are organized into three main groups: Device Interaction, 
        Device Configuration, and FPGA Communication. In a typical application, 
        your software will perform the following steps:
        
        1. Create an instance of okCFrontPanel.
        2. Using the Device Interaction methods, find an appropriate XEM with which 
        to communicate and open that device.
        3. Configure the device PLL (for devices with an on-board PLL).
        4. Download a configuration file to the FPGA using ConfigureFPGA(...).
        5. Perform any application-specific communication with the FPGA using the 
        FPGA Communication methods.    
        """
        return okFrontPanelProxy(self._server)

    def okCFrontPanelDevices(self, realm=''):
        """ Enumerates all the devices available in the given realm. 
    
        The realm of the devices represented by this object. By default, i.e. if
        the value of this argument is an empty string, the realm specified by 
        the okFP_REALM environment variable is used or, if this variable is not 
        defined, the "local" realm.
        """
        return okCFrontPanelDevicesProxy(self._server, realm)

class okCFrontPanelDevicesProxy(object):
    """ Enumerates all the devices available in the given realm. 
   
    The realm of the devices represented by this object. By default, i.e. if 
    the value of this argument is an empty string, the realm specified by 
    the okFP_REALM environment variable is used or, if this variable is not 
    defined, the "local" realm.
    """
    def __init__(self, server, realm=''):
        self._server = server
        self._realm = realm

    def GetCount(self):
        """ Returns the number of available devices, possibly 0. """
        return self._server.get_count(self._realm)

    def GetSerial(self, num=None):
        """ Returns the serial number of the given device, possibly empty if the 
        index is invalid."""
        return self._server.get_serial(self._realm, num)

    def Open(self, serial=None):
        """ Opens the device with the given serial number, first one by default. 
        
        Returns an empty pointer if there is no such device (or no devices at 
        all if the serial is empty).
        """
        realm, serial = self._server.open(self._realm, serial)
        return okFrontPanelProxy(self._server, realm, serial)


class okFrontPanelProxy(object):
    """ This class is the workhorse of the FrontPanel API. 
    
    It's methods are organized into three main groups: Device Interaction, 
    Device Configuration, and FPGA Communication. In a typical application, 
    your software will perform the following steps:
    
    1. Create an instance of okCFrontPanel.
    2. Using the Device Interaction methods, find an appropriate XEM with which 
    to communicate and open that device.
    3. Configure the device PLL (for devices with an on-board PLL).
    4. Download a configuration file to the FPGA using ConfigureFPGA(...).
    5. Perform any application-specific communication with the FPGA using the 
    FPGA Communication methods.    
    """
    def __init__(self, server, realm=None, serial=None):
        self._server = server
        self._realm = realm
        self._serial = serial

    def ConfigureFPGA(self, strFilename):
        """ Download an FPGA configuration from a file.
        
        Args:
            strFilename	(str): A string containing the filename of the 
                configuration file.
        """
        return self._server.configure_fpga(self._realm, self._serial, 
                                           strFilename)

    def GetWireOutValue(self, epAddr):
        """ Gets the value of a particular Wire Out from the internal wire data 
        structure.

        Args:
            epAddr (int): The WireOut address to query.
        """
        return self._server.get_wire_out_value(self._realm, self._serial, 
                                               epAddr)
    
    def IsTriggered(self, epAddr, mask):
        """ Returns true if the trigger has been triggered.

        This method provides a way to find out if a particular bit (or bits) on 
        a particular TriggerOut endpoint has triggered since the last call to 
        UpdateTriggerOuts().

        Args:
            epAddr (int): The TriggerOut address to query.
            mask (int): A mask to apply to the trigger value.
        """
        return self.ok_server.is_triggered(self._realm, self._serial, epAddr, 
                                           mask)

    def OpenBySerial(self, serial=''):
        """ DEPRECIATED: Prefer to use OpalKelly::FrontPanelDevices::Open() 
        in the new code, see Switching to OpalKelly::FrontPanelDevices for more 
        information.

        Args:
            serial (str): The serial number of the device to open.
        """
        self._serial = serial
        return self._server.open_by_serial(serial)

    def SetWireInValue(self, epAddr, val, mask=0xffffffff):
        """ Sets a wire value in the internal wire data structure.

        WireIn endpoint values are stored internally and updated when necessary 
        by calling UpdateWireIns(). The values are updated on a per-endpoint 
        basis by calling this method. In addition, specific bits may be updated 
        independent of other bits within an endpoint by using the optional mask.

        Args:
            epAddr (int): The address of the WireIn endpoint to update.
            val (int): The new value of the WireIn.
            mask (int): A mask to apply to the new value
        """
        return self.ok_server.set_wire_in_value(self._realm, self._serial, 
                                                epAddr, val, mask)

    def UpdateTriggerOuts(self):
        """ Reads Trigger Out endpoints. 
        
        This method is called to query the XEM to determine if any TriggerOuts 
        have been activated since the last call.
        """
        return self._server.update_trigger_outs(self._realm, self._serial)

    def UpdateWireIns(self):
        """ Transfers current Wire In values to the FPGA.

        This method is called after all WireIn values have been updated using 
        SetWireInValue(). The latter call merely updates the values held within 
        a data structure inside the class. This method actually commits the 
        changes to the XEM simultaneously so that all wires will be updated at 
        the same time.
        """
        return self._server.update_wire_ins(self._realm, self._serial)
    
    def UpdateWireOuts(self):
        """ Transfers current Wire Out values from the FPGA.

        This method is called to request the current state of all WireOut values
        from the XEM. All wire outs are captured and read at the same time.
        """
        return self._server.update_wire_outs(self._realm, self._serial)

    def WriteToPipeIn(self, epAddr, data):
        """ Writes a block to a Pipe In endpoint.

        Args:
            epAddr (int): The address of the destination Pipe In.
            data (bytearray): Data to be transferred
        """ 
        return self._server.write_to_pipe_in(self._realm, self._serial, epAddr, 
                                             data)
