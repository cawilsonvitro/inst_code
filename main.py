
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
import dbhandler 

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
        
        #sql stuff app thread will handle sql as it is not continously running
        self.SQL = dbhandler.sql_client("config.json")

        
    
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
        
        self.root = tk.Tk()
        self.root.title("Insturment Control Suite")
        self.root.geometry("430x485")
        self.root.bind("<Escape>", self.endApp)
        self.root.protocol("WM_DELETE_WINDOW",self.endProto)
        self.process_display = tk.StringVar() 
        self.process_display.set("Booting")
        self.root.update_idletasks()
        self.buildGUI(self.root)
        
        self.root.mainloop()
        
        
        pass

    def endApp(self, event):
        '''
        stops app and closes intrument connections
        '''
        self.quit = True
        self.tcphandler.quit()
        self.root.quit()
        
        
        
    def endProto(self):
        '''
        wrapper to end app
        '''
        self.endApp(None)
    #endregion
    #region GUI building
    def buildGUI(self, root):
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
