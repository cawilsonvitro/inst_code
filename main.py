
#region imports
from gui import *
import Eddy as ed
import fourpp as pp
import HMS as hms
import Light as lig
import RDT as rdt
import shutter_one as sh1
import shutter_two as sh2
import Spec_one as spec1
import Spec_two as spec2
import Spec_three as spec3
#endregion
class inst_suite():
    #region application control
    def __init__(self):
        
        self.quit = False
        self.process_display = None

        #spectrometers
        self.NIR = None
        self.CTR = None  #coated side transmission and reflection spectrometer
        self.UTR = None #uncoated side transmission and reflection

        #light contorls

        self.CS = None #coated side shutter
        self.US = None #uncoated side shutter


        #Hall effect
        self.hall = None

        #light control for NIR
        self.light = None

        #RDT 
        self.R_D_T = None

        #resistances
        self.CRM = None #contact sheet R
        self.CLRM = None #contactless sheet R
   
   
    def startApp(self):
        '''
        starts tk application
        '''
        pass

    def loadConfig(self):
        '''
        loads config
        '''
        pass


    def endAPP(self event):
        '''
        stops app and closes intrument connections
        '''
        pass
    #end region
    #region GUI building
    def buildGUI(self):
        '''
        build gui
        '''
        
        pass
    
    #end region

if __name__ == "__main__":
    temp = inst_suite()

    temp.startApp()
