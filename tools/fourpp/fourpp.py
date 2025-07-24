import pyvisa
import logging
import traceback

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
        #logging

        class_name = str(type(self))
        name = class_name.split(" ")[-1][:-1].replace("'", "")
        
        self.logger = logging.getLogger(name)
        
        self.logger.info("4 point probe driver initalized")
        
        
    def init_driver(self):
        self.logger.debug("Init drver")
        self.status = False
        self.logger.debug("starting pyvisa rm")
        self.rm = pyvisa.ResourceManager()

        
        self.logger.debug(f"Connecting to instrument at {self.inst_addy}")
        self.instrument = self.rm.open_resource(self.inst_addy, timeout = (self.sam_count*1000))
        
        self.instrument.read_termination = '\n'
        self.instrument.write_termination = '\n'

        try:
            self.instrument.query('*IDN?')
            self.logger.debug("Driver successfully communicated to intrument")
            self.status = True
        except Exception as e:
            print(e)
            self.logger.error(traceback.format_exc())
            self.status = False

        #setting up params
        self.logger.debug("setting up parameters")
        self.instrument.write('CONF:FRES ')
        self.instrument.write('SAMP:COUN 1')
        self.instrument.write('TRIG:SOUR IMM')
        self.res_zero = self.instrument.query('READ?')
        
        #setting sample count
        self.logger.debug(f"setting number of samples to be taken to {self.sam_count}")
        self.instrument.write('SAMP:COUN ' + str(self.sam_count))

        self.logger.debug("init complete")
        #take test reading. 
    def measure(self):
        self.logger.debug("requesting read")
        self.values_raw = self.instrument.query('READ?')

        self.logger.debug(f"data recv from {self.inst_addy}, processing")
        values_str = [item.strip() for item in self.values_raw.split(',')]

        self.values = [float(r1) for r1 in values_str]


        

    def quit(self):
        self.logger.debug("shutting down instrument")
        self.instrument.close()
        if 'rm' in locals():
                self.rm.close()




if __name__ == "__main__":
    def convert(value):
        answer = value * 4.517 * 1 * 1.006
        print(answer)
    
    foo = siglent("USB0::0xF4EC::0x1208::SDM36HCD801150::INSTR")

    foo.init_driver()

    foo.measure()
    print(foo.values)
    foo.quit()

    value = sum(foo.values)/len(foo.values)
    
    convert(value)



    


