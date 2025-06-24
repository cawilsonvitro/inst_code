import matplotlib.pyplot as plt
from stellarnet_driverLibs import stellarnet_driver3 as sn

class StellarnetError(Exception):
    
    def __init__(self, message):
        super().__init__(message)
    
    def __str__(self):
        return self.message
    
    pass
class stellarnet():

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
        
        
        self.wav = None
        self.spectra: list[float|int] = None


    def init_driver(self):
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
        self.spectra = sn.getSpectrum_Y(self.spec)
        

    def quit(self):
        self.status = False
        sn.reset(self.spec)
        
if __name__ == "__main__":
    
    
    spec = stellarnet(int_time = 50, scans_to_avg = 1, x_smooth = 0,  x_timing = 3)
    
    spec.init_driver()
    
    spec.measure()
    
    spec.quit()
    
    
    




