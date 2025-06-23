import pyvisa
import numpy as np
import random

class rdt_sys():

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

    def init_driver(self):
        self.status = True
    
    def measure(self):
        self.values = [[7,8,9,10]]

        

    def quit(self):
        self.status = False
        



# foo = siglent("USB0::0xF4EC::0x1208::SDM36HCD801150::INSTR")

# foo.init_driver()

# foo.measure()

# foo.quit()

# value = sum(foo.values)/len(foo.values)


# def convert(value):
#     answer = 4.517 * 0.6337 
    


