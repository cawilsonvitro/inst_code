
#region imports
from gui_package_cawilvitro import *
import socket
from multiprocessing import Process, Queue
from queue import Empty
import time
import json
import sys

#endregion
class inst_suite():
    #region app init
    def __init__(self,):
        
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

        
        #tcp vars
        self.host = sys.argv[1]
        print(self.host)
        self.port = 5000
        
    
    
    
        def loadConfig(self):
            '''
            loads config
            '''
            pass
        
    
    def setup(self) -> None:
        '''
        setups all threads for main application
        '''
        
        self.message: Queue[Any] = Queue(maxsize=1)
        self.response: Queue[Any] = Queue(maxsize=1)
        
        self.appThread = Process(target=self.startApp, args=())
        self.tcpThread = Process(target=self.TCPServer, args=())
    
    
    #endregion
    #region application control
    
   
    def startApp(self):
        '''
        starts tk application
        '''
        
        
        pass

    def endAPP(self, event):
        '''
        stops app and closes intrument connections
        '''
        pass
    #endregion
    #region GUI building
    def buildGUI(self):
        '''
        build gui
        '''
        
        pass
    
    #endregion
    #region tcp server

    def TCPServer(self):
        '''
        starts tcp server
        '''

    #endregion  


if __name__ == "__main__":
    temp = inst_suite()

    # temp.startApp()
    