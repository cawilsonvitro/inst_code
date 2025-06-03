
#region imports
from gui_package_cawilvitro import *
import socket
import select
from multiprocessing import Process, Queue
from queue import Empty
import time
import json
import sys
import tcp_class 
import threading

#endregion
class inst_suite():
    #region app init
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

        
        #tcp vars
        self.host = sys.argv[1]
        self.port = 5050
        self.ADDR = (self.host, self.port)
        

        
    
    def setup(self) -> None:
        '''
        setups all threads for main application
        '''
        
        self.message: Queue[Any] = Queue(maxsize=1)
        self.response: Queue[Any] = Queue(maxsize=1)
        self.tcphandler: tcp_class.tcp_multiserver = tcp_class.tcp_multiserver(self.host, self.port, self.message, self.response)
        
        
        self.appThread = threading.Thread(target=self.startApp, args=())
        self.tcpThread = threading.Thread(target=self.tcphandler.server, args=())
        self.insturmentManagerThread = threading.Thread(target=self.test, args=())
        
        self.appThread.daemon = True
        self.tcpThread.daemon = True
        self.insturmentManagerThread.daemon = True
        
        #starting threads
        self.appThread.start()
        self.tcpThread.start()
        self.insturmentManagerThread.start()
        
        self.appThread.join()
        self.tcpThread.join()
        self.insturmentManagerThread.join()
    #    
    
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
        self.quit = True
    #endregion
    #region GUI building
    def buildGUI(self):
        '''
        build gui
        '''
        
        pass
    
    #endregion
    #region inst manager
    
    def test(self):
        '''
        manages all instruments and instrument communications
        '''
        while not self.quit:
            #getting tcp message
            try:
                msg = self.message.get(block=False)
            except Empty:
                continue
            # returning response to the client
            try:
                self.response.put("Response from main app")
            except Exception as e:
                print(f"Error putting response in queue: {e}")
        
    #endregion  


if __name__ == "__main__":
    
    temp = inst_suite()
    temp.setup()
