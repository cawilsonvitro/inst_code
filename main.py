
#region imports
from gui_package_cawilvitro import *
import socket

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
        self.host = None
        self.port = None
        
    #endregion
    #region application control
   
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
    def startTCPServer(self):
        '''
        starts tcp server
        '''
        self.host = socket.gethostname()
        self.port = 5000
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server started at {self.host}:{self.port}")
        conn, addr = self.server_socket.accept()
        print(f"Connection from {addr} has been established.")

    #endregion  


if __name__ == "__main__":
    temp = inst_suite()

    temp.startApp()
    
    print("I ran")
