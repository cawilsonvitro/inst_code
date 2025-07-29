#region imports
from gui_package_cawilvitro import *
from instutil import inst_util as iu
import nearir as IR
from tkinter import Misc
import tkinter.ttk as ttk
from multiprocessing import Process, Queue
from queue import Empty
import time
import json
import sys
import threading
from datetime import datetime as dt
import traceback
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
        TimedRotatingFileHandler(f'tools\\nearir\\logs\\{date}.log', when = "D", backupCount= 5)
    ]
)


#endregion

class near_ir_app():
    
    #region application start up
    def __init__(self, ip, port):
        '''
        init class for use
        '''
        self.quit = False
        
        self.process_display = None
        self.samples = []
        
        #spectrometer
        self.spectrometer = None

        #data management
        self.value = None
        self.dataPath = r"data/"
        self.sample_num:int
        self.exst = ".csv"
        self.fmanager:iu.FileManager = iu.FileManager("nearir", "5")
        self.description: str = "None"
        #threading
        # self.message: Queue[Any] = Queue(maxsize=1)
        # self.response: Queue[Any] = Queue(maxsize=1)
        
        #logging

        class_name = str(type(self))
        name = class_name.split(" ")[-1][:-1].replace("'", "")
        
        self.logger = logging.getLogger(name)
        
        self.logger.info("4 point probe app initalized")
        
        #tcp 
        self.ip, self.port = (ip, port)  
        

    
    def connectClient(self) -> None:
        self.logger.info(f"Connecting to server {self.ip}:{self.port}")
        self.connected:bool = False
        
        
        try:            
            self.tcp = iu.client(self.ip, self.port)#, self.message, self.response)
            result = self.tcp.connect()
            if result != None:
                self.connection = False
                self.logger.error(traceback.format_exc())
            else:
                self.logger.info("Connect to server")
                self.connected = True
        except Exception as e:
            traceback.print_exc()
            self.connected = False
            
        if self.connected:
            self.logger.info(f"Connected to server {self.ip}:{self.port}")
            StandardLabel.instances["Connection"].configure(image = TkImage("connection_status", r"images\Status_Good.png").image)
            try:
                self.tcp.id()
            except Exception as e:
                self.logger.error(f"Failed to send id to server")
        else:
            StandardLabel.instances["Connection"].configure(image = TkImage("connection_status", r"images\Status_Bad.png").image)
            self.logger.error(f"Failed to connect to server, see above for details")
    
    def startApp(self):
        self.logger.info("Starting NIR app")
        self.root = tk.Tk()
        self.root.title("NIR measurement")
        self.root.geometry("480x240")
        self.root.resizable(width=False,height=False)
        self.root.bind("<Escape>", self.endApp)
        self.root.protocol("WM_DELETE_WINDOW",partial(self.endApp, None))
        self.process_display = tk.StringVar() 
        self.process_display.set("Booting")
        self.root.update_idletasks()
        self.buildGUI(self.root)
        self.connectClient()
        self.logger.info("GUI built, starting main loop")
        self.root.mainloop()
    
    #endregion
    
    #region app control  
    
    def endApp(self, event):
        '''
        ends application
        '''
        self.logger.info("Shutting down application")
        self.quit = True
        try:
            if self.connected: 
                self.tcp.disconnect()
        except:
            self.logger.debug("client already shut down")
        self.spectrometer.quit()
        self.root.quit()
        
        
    #endregion
   
    #region  GUI
        
    def toggle_desc(self):
        self.logger.info("Toggling Description Window")
        state = self.desc_window.state()
        if state == "normal": self.desc_window.withdraw()
        if state == "withdrawn": self.desc_window.deiconify()

    
    def get_desc(self, event) ->None:
        #closes out window and gets info
        self.description = TextBox.instances["desc"].get("1.0","end-1c")
        TextBox.instances["desc"].delete("1.0","end-1c")
        self.toggle_desc()
        
        self.wait.set(False)
        
    def update(self) -> None:
        self.logger.info("Updating sample dropdown")
        self.tcp.soc.send("UPDATE".encode())
        resp:str = self.tcp.soc.recv(1024).decode()
        print(resp)
        if resp != "None":
            dropdown.instances["samples"].configure(values=resp.split(","))
        else:
            dropdown.instances["samples"].configure(values=[])
        
    def buildGUI(self, root):
        '''
        builds gui for user interaction
        '''
        self.logger.info("Building GUI")
        Button.remove(None)
        Label.remove(None)
        StandardLabel.remove(None)
        dropdown.remove(None)
        
        #to track our var
        self.wait:tk.BooleanVar = tk.BooleanVar()
        
        self.wait.set(False)
        
        #main window
        
        dropdown(
            "samples",
            root,
            values = "",
            width = 28,
            postcommand= self.update,
        ).place(x = 0, y = 60)
        dropdown(
            "position",
            root,
            values = ["LT", "LC", "LL", "CT", "CC", "CL", "RT", "RC", "RL"],
            width = 5,
        ).place(x = 200, y = 60)
        
        Label(
            "positions",
            root,
            text = "position:",
            anchor=tk.W,           
            height=1,              
            width=30,              
            bd=1,                  
            font=("Arial", 10), 
            cursor="hand2",   
            fg="black",                           
            justify = tk.LEFT,  
            wraplength=100   
            ).place(x = 200, y = 40, width = 80,height = 20)
        
        Label(
            "Samples",
            root,
            text = "sample ID:",
            anchor=tk.W,           
            height=1,              
            width=30,              
            bd=1,                  
            font=("Arial", 10), 
            cursor="hand2",   
            fg="black",                           
            justify = tk.LEFT,  
            wraplength=100   
            ).place(x = 0, y = 40, width = 80,height = 20)
        
        
        StandardButtons(
            "Measure",
            root,
            image = TkImage("Measure", r"tools\nearir\images\Measure_Button.png").image,
            command = self.measure
        ).place(x = 0, y = 120)
        
        StandardButtons(
            "Reconnect",
            root,
            image = TkImage("Reconnect", r"tools\nearir\images\Reconnect_Button.png").image,
            command = self.connectClient
        ).place(x = 0, y = 190)
        
        StandardLabel(
            "Connection",
            root,
            image = TkImage("Connect_status",  r"tools\nearir\images\Status_Bad.png").image
        ).place(x = 140, y = 190)
        
        Label(
            "Process_Status", 
            root,
            textvariable = self.process_display,
            anchor=tk.W,           
            height=1,              
            width=30,              
            bd=1,                  
            font=("Arial", 10), 
            cursor="hand2",   
            fg="black",                           
            justify = tk.LEFT,  
            wraplength=100   
            ).place(x = 300, y = 40, width = 180,height = 200)
        
        StandardLabel(
            "Status",
            root,
            image = TkImage("status_bad", r"tools\nearir\images\Status_Bad.png").image
        ).place(x = 140, y = 120)
        
        #description window
        TextBox.remove(None) #here so we only have to call this once might havet to switch
        self.desc_window = tk.Toplevel(self.root)
        self.desc_window.geometry("300x800")
        self.desc_window.title("Sample Description")
        self.desc_window.bind('<<Escape>>', self.get_desc)
        self.desc_window.protocol("WM_DELETE_WINDOW", partial(self.get_desc, None))
        TextBox("desc", self.desc_window, height = 20, width = 32).place(x = 10, y = 50)
        self.desc_window.withdraw()
        
        self.process_display.set("GUI Built, initalizing Driver")
        self.logger.info("GUI built, initializing Driver")
        self.init_spec()

    #endregion
    
    #region spectrometer
    def init_spec(self):
        self.logger.info("Loading driver")
        self.process_display.set("Loading Driver")
        self.root.update_idletasks()
        try:
            self.spectrometer = IR.stellarnet(int_time=1000, scans_to_avg=1, x_smooth=0, x_timing=3)
            self.spectrometer.init_driver()
            
        except Exception as e:
            traceback.print_exc()
            
        if self.spectrometer.status:
            StandardLabel(
                "Status",
                self.root,
                image = TkImage("status_Bad",r"tools\nearir\images\Status_Good.png").image,
            ).place(x = 140, y = 120)
            self.logger.info("Driver loaded successfully")
        else:
            StandardLabel(
                "Status",
                self.root,
                image = TkImage("status_bad", r"tools\nearir\images\Status_Bad.png").image
            ).place(x = 140, y = 120)
            self.logger.error("Failed to load driver, see above for details")
        self.process_display.set("Drivers loaded, Ready")
    
    #endregion
    
    #region data management
    def tcp_proptocol(self) -> None:
        self.logger.info("Starting TCP protocol")
        
        self.logger.debug("Sending META command to server")
        self.tcp.soc.send("META".encode())
        resp = self.tcp.soc.recv(1024).decode()
        self.logger.debug(f"Received response: {resp}")
        self.logger.debug("Sending sample number to server")
        self.tcp.soc.send(str(self.sample_num).encode())
        self.description = self.tcp.soc.recv(1024).decode()
        self.logger.debug(f"got {self.description} from server")
        TextBox.instances["desc"].insert("1.0", self.description)
        self.logger.debug(f"Server sent sample description {self.description}, launched description editor")
        self.process_display.set("Please enter sample, if no description needed enter none")
        self.wait.set(True)
        self.toggle_desc()
        self.root.wait_variable(self.wait)
        self.logger.debug(f"user set description to {self.description}")

        self.logger.info("Starting TCP MEAS protocol")

        self.logger.debug("Sending MEAS command")
        self.tcp.soc.send("MEAS".encode())
        resp = self.tcp.soc.recv(1024).decode()
        self.logger.debug(f"got {resp} from Server")
        self.logger.debug(f"sending sample id {self.sample_num}")
        self.tcp.soc.send(self.sample_num.encode())
        resp = self.tcp.soc.recv(1024).decode()
        self.logger.debug(f"Received response: {resp}")
        self.tcp.soc.send(self.description.encode())
        resp = self.tcp.soc.recv(1024).decode()
        self.logger.debug(f"Received response: {resp}")
        self.tcp.soc.send(str(self.value).encode())
        resp = self.tcp.soc.recv(1024).decode()
        self.logger.debug(f"Received response: {resp}")
        if resp != "data received":
           self.logger.error(f"unexcpeted response from server {resp}")
        else:
            self.logger.info("TCP protocol complete")



    
    #endregion
    
    #region measurement
    def measure(self):
        self.logger.info("starting measurement")
        self.process_display.set("measuring")
        self.sample_num:str = dropdown.instances["samples"].get()
        self.logger.info(f"Sample: {self.sample_num}")
        if self.sample_num == "":
            self.process_display.set("Please select or enter a sample ID")
        else:
            if self.DM.status:
                try:
                    self.DM.measure()
                    self.value = (sum(self.DM.values)/len(self.DM.values)) * 4.517 * 1 * 1.006
                    if self.connected:
                        self.tcp_proptocol()
                    self.process_display.set("Ready")
                except Exception as e:
                    traceback.print_exc()
                    self.DM.status = False
                    print("Measuring fail", e)
            data:list[str | int | float] = [self.sample_num, str(dt.now()), self.value]
            
            
            if not self.connected: #always get a sample description if not connected
                self.logger.info("Not connected to server, having user manual enter sample description")
                self.wait.set(True)
                self.toggle_desc()
                self.root.wait_variable(self.wait)
            
            
            
            data.append(self.description)
            self.fmanager.write_data("nearir", ["sample id", "time", "resistance", "description"], [data])
                
            
            
            if not self.DM.status:
                self.init_spec()
    #endregion
    

    #region threading
    
        
        
    #endregion
if __name__ == "__main__":
    logging.info("start from main")
    try:
        SERVER = sys.argv[1]
    except:
        # SERVER = "127.0.0.1" 
        SERVER = "192.168.1.1"
    
    PORT = 5050
    ADDR = (SERVER, PORT)
    
    temp = near_ir_app(SERVER, PORT)
    temp.startApp()

 