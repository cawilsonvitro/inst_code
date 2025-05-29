import pyvisa
import numpy as np

class siglent():

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
        self.status = False
        self.rm = pyvisa.ResourceManager()

        self.instrument = self.rm.open_resource(self.inst_addy, timeout = (self.sam_count*1000))
        
        self.instrument.read_termination = '\n'
        self.instrument.write_termination = '\n'

        try:
            self.instrument.query('*IDN?')
            self.status = True
        except Exception as e:
            print(e)
            self.status = False

        #setting up params
        self.instrument.write('CONF:FRES ')
        self.instrument.write('SAMP:COUN 1')
        self.instrument.write('TRIG:SOUR IMM')
        self.res_zero = self.instrument.query('READ?')
        
        #setting sample count
        self.instrument.write('SAMP:COUN ' + str(self.sam_count))

        #take test reading. 
    def measure(self):
        self.values_raw = self.instrument.query('READ?')

        values_str = [item.strip() for item in self.values_raw.split(',')]

        self.values = [float(r1) for r1 in values_str]


        print(self.values)

        

    def quit(self):
        self.instrument.close()
        if 'rm' in locals():
                self.rm.close()



foo = siglent("USB0::0xF4EC::0x1208::SDM36HCD801150::INSTR")

# foo.init_driver()

# foo.measure()

# foo.quit()

# value = sum(foo.values)/len(foo.values)


# def convert(value):
#     answer = 4.517 * 0.6337 
    


