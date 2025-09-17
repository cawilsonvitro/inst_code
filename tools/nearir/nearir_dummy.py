import pyvisa
import numpy as np
import random
import time as t
class stellarnet():

    def __init__(self,connection_string, **kwargs):
        
        self.status = False
        
        self.rm = None
        self.inst_addy = connection_string
        self.instrument = None
        
        
        self.res_zero = None
        self.sam_count = 30

        self.values = None
        self.values_raw = None

        self.std = None
                
        self.wv = ["a","b","c"]
        self.spectra: list[float|int] = [str(i) for i in range(0,len(self.wv))]
    def init_driver(self):
        self.status = True
    
    def measure(self):
        self.values = [[7,8,9,10]]
        t.sleep(5)

    def quit(self):
        self.status = False
        


if __name__ == "__main__":
    temp = stellarnet("USB0::0xF4EC::0x1208::SDM36HCD801150::INSTR", int_time=1000, scans_to_avg=1, x_smooth=0, x_timing=3)
    
    print(temp.spectra)
# foo = siglent("USB0::0xF4EC::0x1208::SDM36HCD801150::INSTR")

# foo.init_driver()

# foo.measure()

# foo.quit()

# value = sum(foo.values)/len(foo.values)


# def convert(value):
#     answer = 4.517 * 0.6337 
    


