import matplotlib.pyplot as plt
from stellarnet_driverLibs import stellarnet_driver3 as sn

class StellarnetError(Exception):
    """
    Custom exception class for handling errors related to Stellarnet operations.
    Attributes:
        message (str): Description of the error.
    Args:
        message (str): Human-readable message describing the error.
    Example:
        raise StellarnetError("Failed to connect to Stellarnet device.")
    """
    
    def __init__(self, message):
        super().__init__(message)
        self.message = message
    
    def __str__(self):
        return self.message
    
    pass

class stellarnet():
    """
    Class for interfacing with a Stellarnet spectrometer device.
    Attributes:
        status (bool): Indicates the current status of the device connection.
        spec: The spectrometer device handle.
        deviceID: The unique identifier for the connected device.
        kwargs (dict): Keyword arguments for spectrometer configuration.
        inittime: Integration time parameter from kwargs.
        scansavg: Number of scans to average from kwargs.
        smooth: Smoothing parameter from kwargs.
        xtiming: Timing parameter from kwargs.
        wav: Wavelength data (to be set after initialization).
        spectra (list[float|int]): Latest measured spectra data.
    Methods:
        __init__(**kwargs):
            Initializes the Stellarnet spectrometer object with configuration parameters.
        init_driver():
            Initializes the spectrometer driver, connects to the device, sets parameters,
            and verifies configuration. Raises StellarnetError if parameters do not match.
        measure():
            Acquires a spectrum from the spectrometer and stores it in self.spectra.
        quit():
            Resets the spectrometer and marks the device as disconnected.
    """

    def __init__(self, **kwargs):
        self.status = False
        
        #for spec
        self.spec = None
        self.deviceID = None
        
        #spef for stellarnet
        self.kwargs = kwargs
        self.inittime = self.kwargs["int_time"]
        self.scansavg = self.kwargs["scans_to_avg"]
        self.smooth = self.kwargs["x_smooth"]
        self.xtiming = self.kwargs["x_timing"]
        
        
        self.wv = None
        self.spectra: list[float|int] = None


    def init_driver(self):
        """
        Initializes the spectrometer driver and validates device parameters.
        Attempts to connect to the spectrometer, retrieve its specifications, and set initial parameters.
        Compares the current device parameters with the expected values provided in `self.kwargs`.
        If any parameter does not match, raises a StellarnetError.
        Sets the status flag to True if initialization is successful, otherwise sets it to False.
        Raises:
            StellarnetError: If any device parameter does not match the expected value.
            Exception: For any other errors encountered during initialization.
        """
        self.status = False
        
        try:
            version = sn.version()
            self.spec, self.wv = sn.array_get_spec(0)  # 0 for first channel and 1 for second channel, up to 127 spectrometers  
            self.deviceID = sn.getDeviceId(self.spec)
            sn.setParam(self.spec, self.inittime, self.scansavg, self.smooth, self.xtiming, True)
            params = sn.getDeviceParam(self.spec)
            
            
            for key in self.kwargs.keys():
                if self.kwargs[key] != params[key]:
                    raise StellarnetError(f"Parameter {key} does not match. Expected {self.kwargs[key]}, got {params[key]}")
            
            
            first_data = sn.array_spectrum(self.spec, self.wv)
        
            self.status = True
            
            
        except Exception as e:
            print(f"error: {e}")
            self.status = False
            
        
    
    def measure(self):
        """
        Measures and retrieves the spectrum data using the spectrometer.

        This method calls the `getSpectrum_Y` function from the `sn` module,
        passing the current spectrometer instance (`self.spec`) as an argument.
        The resulting spectrum data is stored in the `self.spectra` attribute.
        """
        self.spectra = sn.getSpectrum_Y(self.spec)
        

    def quit(self):
        """
        Terminates the current process by setting the status to False and resetting the spectrometer.

        This method updates the object's status attribute to indicate that the process should stop,
        and calls the reset function from the 'sn' module to reset the spectrometer specified by self.spec.
        """
        self.status = False
        sn.reset(self.spec)
        
if __name__ == "__main__":
    spec = stellarnet(int_time = 50, scans_to_avg = 1, x_smooth = 0,  x_timing = 3)
    spec.init_driver()
    spec.measure()
    spec.quit()
    
    
    




