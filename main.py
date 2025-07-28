
#region imports
from gui_package_cawilvitro import * #type:ignore
import socket
from queue import Empty #type:ignore
import json
import sys
from instutil import inst_util as iu
import threading
from socket import socket
from datetime import datetime as dt
import logging
from logging.handlers import TimedRotatingFileHandler
from functools import partial
#endregion

#region logging
date = dt.now().strftime("%m-%d-%Y, Hour %H Min %M Sec %S")

logging.basicConfig(
    level=logging.DEBUG, # Set a global logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.StreamHandler(), # Log to console
        TimedRotatingFileHandler(f'logs\\{date}.log', when = "D", backupCount= 5)
    ]
)
#end region

class inst_suite():
    #region app init
    def __init__(self):
        
        self.quit = False
        self.process_display = None
        self.teststr = "HIIIII"
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
        self.test = "HI"
        #resistances
        self.CRM = None #contact sheet R
        self.CLRM = None #contactless sheet R
        #logging

        class_name = str(type(self))
        name = class_name.split(" ")[-1][:-1].replace("'", "")
        
        self.logger = logging.getLogger(name)
        self.logger.info("Server initalized")
        #tcp vars
        try:
            self.host = sys.argv[1]
        except:
            self.host = "192.168.1.1"
        self.port = 5050
        self.ADDR = (self.host, self.port)
        self.configpath = 'config.json'
        with open(self.configpath , 'r') as file:
            self.toolip:dict[str,str] = json.load(file)['Tool_ip']
        self.tools:list[str] = list(self.toolip.values())
        
        #sql stuff app thread will handle sql as it is not continously running
          
    def setup(self) -> None:
        '''
        setups all threads for main application
        '''
        
        # self.message: Queue[Any] = Queue(maxsize=1)
        # self.response: Queue[Any] = Queue(maxsize=1)
        
        #setting up tcp server and getting instruments
        self.tcphandler: iu.tcp_multiserver = iu.tcp_multiserver(self.configpath, self.host, self.port, self)#, self.message, self.response)
        self.tcphandler.SQL_startup()
        
        self.appThread = threading.Thread(target=self.startApp, args=())
        self.tcpThread = threading.Thread(target=self.tcphandler.server, args=())
        # self.insturmentManagerThread = threading.Thread(target=self.test, args=())
        
        self.appThread.daemon = True
        self.tcpThread.daemon = True
        # self.insturmentManagerThread.daemon = True
        
        #starting threads
        self.appThread.start()
        self.tcpThread.start()
        # self.insturmentManagerThread.start()
        
        self.appThread.join()
        self.tcpThread.join()
        # self.insturmentManagerThread.join()
        
        #cwd to fix issues
        
    #    
    
    #endregion
    #region application control   
   
    def startApp(self):
        '''
        starts tk application
        '''
        
        self.root: tk.Tk = tk.Tk() 
        self.root.title("Insturment Control Suite")
        self.root.geometry("430x485")
        self.root.bind("<Escape>", self.endApp) #type: ignore
        self.root.protocol("WM_DELETE_WINDOW",partial(self.endApp, None))
        self.process_display = tk.StringVar() 
        self.process_display.set("Booting")
        self.root.update_idletasks()
        self.buildGUI(self.root)
        self.test_connections()
        self.root.mainloop()
        
         #checks inst connections before booting up tcp server and other 
        pass

    def endApp(self, event: Any):
        '''
        stops app and closes intrument connections
        '''
        self.quit = True
        self.tcphandler.quit()
        self.root.quit()
        sys.exit(0)
    #endregion
    
    #region GUI building
    def buildGUI(self, root: tk.Tk) -> None:
        '''
        build gui
        '''
        StandardLabel.remove(None)
        
        StandardLabel (
            "hall",
            root,
            image = TkImage("hall_label", r"images\hall_label.png").image
        ).place(x = 50, y = 5)
        
        StandardLabel (
            "hall_status",
            root,
            image = TkImage("hall_status", r"images\Status_Bad.png").image
        ).place(x = 198, y = 10)
        
        StandardLabel (
            "4pp",
            root,
            image = TkImage("4pp_label", r"images\4pp_label.png").image
        ).place(x = 50, y = 75)
        
        StandardLabel(
            "fourpp_status",
            root,
            image = TkImage("fourpp_status", r"images\Status_Bad.png").image
        ).place(x = 198, y = 80)
        
        StandardLabel (
            "rdt",
            root,
            image= TkImage("rdt_label", r"images\rdt_label.png").image
        ).place(x = 50, y = 145)
        
        StandardLabel(
            "rdt_status",
            root,
            image = TkImage("rdt_status_bad", r"images\Status_Bad.png").image
        ).place(x = 198, y = 150)
        
        StandardLabel (
            "nearir",
            root,
            image= TkImage("nearir_label", r"images\nir_label.png").image
        ).place(x = 50, y = 215)
        
        StandardLabel (
            "nearir_status",
            root,
            image= TkImage("nearir_status", r"images\Status_Bad.png").image
        ).place(x = 198, y = 220)
        
        StandardLabel (
            "SQL",
            root,
            image= TkImage("SQL_label", r"images\sql_label.png").image
        ).place(x = 50, y = 350)
        
        StandardLabel (
            "SQL_status",
            root,
            image= TkImage("SQL_status", r"images\Status_Bad.png").image
        ).place(x = 210, y = 355)
        
        StandardLabel (
            "Network",
            root,
            image= TkImage("Net_label", r"images\network_label.png").image
        ).place(x = 50, y = 400)
        
        StandardLabel (
            "Net_status",
            root,
            image= TkImage("Net_status", r"images\Status_Bad.png").image
        ).place(x = 210, y = 405)
        
        StandardButtons(
            "Test",
            root,
            image = TkImage("Test", r"images\test_connections.png").image,
            command = self.test_connections,
        ).place(x = 50, y = 300)
    
    #endregion
    #region inst manager
    
    def test_connections(self):
        '''
        manages all instruments and instrument communications
        '''
        # StandardLabel.instances["fourpp_status"].configure(image = TkImage("fourpp_status", r"images\Status_Bad.png").image)

        # first testing internet connections
        self.tcphandler.connections()
        print("Testing connections")
        self.net_stat = self.tcphandler.network_status
        self.db_stat = self.tcphandler.db_status
        
        if self.net_stat:
            StandardLabel (
                "Net_status",
                self.root,
                image= TkImage("Net_status", r"images\Status_Good.png").image
            ).place(x = 210, y = 405)
        else:
            StandardLabel (
                "Net_status",
                self.root,
                image= TkImage("Net_status", r"images\Status_Bad.png").image
            ).place(x = 210, y = 405)

        if self.db_stat:
            StandardLabel (
                "SQL_status",
                self.root,
                image= TkImage("SQL_status", r"images\Status_Good.png").image
                ).place(x = 210, y = 355)
        else:
            StandardLabel (
                "SQL_status",
                self.root,
                image= TkImage("SQL_status", r"images\Status_Bad.png").image
            ).place(x = 210, y = 355)
        
        #testing instrument connections
        conc_clients: list[socket] = self.tcphandler.connected_sockets
        conc_tools: list[str] = [self.toolip[soc.getpeername()[0]] for soc in conc_clients]

        for tool in self.tools:
            try:
                if tool in conc_tools:
                    StandardLabel.instances[f"{tool}_status"].configure(image = TkImage(f"{tool.lower()}_status", r"images\Status_Good.png").image)
                else:
                    StandardLabel.instances[f"{tool}_status"].configure(image = TkImage(f"{tool.lower()}_status", r"images\Status_Bad.png").image)
            except KeyError:
                print(f" {tool} not integrated into Front end")
        self.root.update()
    # endregion  


if __name__ == "__main__":
    
    temp = inst_suite()
    temp.setup()
