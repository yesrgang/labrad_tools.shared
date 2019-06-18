

class LJMProxy(object):
    def __init__(self, server):
        self._server = server

    def openS(self, deviceType='ANY', connectionType='ANY', identifier='ANY'):
        """ Opens a LabJack device, and returns the device handle.
        
        Args:
            deviceType: A string containing the type of the device to be
                connected, optionally prepended by "LJM_dt". Possible values
                include "ANY", "T4", "T7", and "DIGIT".
            connectionType: A string containing the type of the connection
                desired, optionally prepended by "LJM_ct". Possible values
                include "ANY", "USB", "TCP", "ETHERNET", and "WIFI".
            identifier: A string identifying the device to be connected or
                "LJM_idANY"/"ANY". This can be a serial number, IP address,
                or device name. Device names may not contain periods.
        
        Returns:
            The new handle that represents a device connection upon success.
        
        Raises:
            TypeError: deviceType or connectionType are not strings.
            LJMError: An error was returned from the LJM library call.
        
        Note:
            Args are not case-sensitive, and empty strings indicate the
            same thing as "LJM_xxANY".
        """
        return self._server.open_s(deviceType, connectionType, identifier)

    def eReadName(self, handle, name):
        """ Performs Modbus operations that reads a value from a device.
        
        Args:
            handle: A valid handle to an open device.
            name: A name (string) to read.
        
        Returns:
            The read value.
        
        Raises:
            TypeError: name is not a string.
            LJMError: An error was returned from the LJM library call.
        """ 
        return self._server.e_read_name(handle, name)
