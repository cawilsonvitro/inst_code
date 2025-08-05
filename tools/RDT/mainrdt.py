#region imports
from gui_package_cawilvitro import *
from instutil import inst_util as iu
import RDT as RDT
# import RDT_dummy as RDT
import tkinter as tk#region imports
from gui_package_cawilvitro import *
from instutil import inst_util as iu
import RDT as rdt_Driver
# import RDT_dummy as rdt_Driver
import tkinter as tk
import sys
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
        TimedRotatingFileHandler(f'tools\\RDT\\logs\\{date}.log', when = "D", backupCount= 5)
    ]
)


#endregion

class rdt_app():
    
    #region application start up
    def __init__(self, ip, port, T_bias_on, t_run, t_delay,fan_delay, T_cool, num_of_meas, min_val, max_val):
        '''
        init class for use
        '''
        self.quit = False
        
        self.process_display = None
        self.c1 = None
        self.t1 = None
        self.t2 = None
        self.samples = []
        #RDT driver
        self.rdt = None
        self.T_bias_on = T_bias_on
        self.t_run = t_run
        self.t_delay = t_delay
        self.fan_delay = fan_delay
        self.T_cool = T_cool
        self.num_of_meas = num_of_meas
        self.min_val = min_val
        self.max_val = max_val


        #data management
        self.value = None
        self.dataPath = r"data/"
        self.sample_num:int
        self.exst = ".csv"
        self.fmanager:iu.FileManager = iu.FileManager("RDT", "5")
        self.description: str = "None"
        #threading
        # self.message: Queue[Any] = Queue(maxsize=1)
        # self.response: Queue[Any] = Queue(maxsize=1)
        
        #logging

        class_name = str(type(self))
        name = class_name.split(" ")[-1][:-1].replace("'", "")
        
        self.logger = logging.getLogger(name)
        
        self.logger.info("rdt app initalized")
        
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
        self.logger.info("Starting rdt app")
        self.root = tk.Tk()
        self.root.title("rdt measurement")
        self.root.geometry("480x240")
        self.root.resizable(width=False,height=False)
        self.root.bind("<Escape>", self.endApp)
        self.root.protocol("WM_DELETE_WINDOW",partial(self.endApp, None))
        self.process_display = tk.StringVar()
        self.c1 = tk.StringVar()
        self.t1 = tk.StringVar()
        self.t2 = tk.StringVar()
        self.process_display.set("Booting")
        self.c1.set("0.0")
        self.t1.set("0.0")  
        self.t2.set("0.0")
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
            self.rdt.quit()
            self.root.quit()
            if self.connected: 
                self.tcp.disconnect()
        except:
            self.logger.debug("client already shut down")
       
        
        
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
    
    def get_pos(self,event) -> None:        
        self.logger.debug("Getting pos")
        self.position = "" 
        self.position = dropdown.instances["position"].get()
        self.logger.debug(f"{self.position} selected")
        
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
            postcommand = self.update,
        ).place(x = 0, y = 60)
        dropdown(
            "position",
            root,
            values = ["LT", "LC", "LL", "CT", "CC", "CL", "RT", "RC", "RL"],
            width = 5,
        ).place(x = 200, y = 60)
        dropdown.instances["position"].bind('<<ComboboxSelected>>', self.get_pos)
        
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
            image = TkImage("Measure", r"tools\RDT\images\Measure_Button.png").image,
            command = self.measure
        ).place(x = 0, y = 120)
        
        StandardButtons(
            "Reconnect",
            root,
            image = TkImage("Reconnect", r"tools\RDT\images\Reconnect_Button.png").image,
            command = self.connectClient
        ).place(x = 0, y = 190)
        
        StandardLabel(
            "Connection",
            root,
            image = TkImage("Connect_status",  r"tools\RDT\images\Status_Bad.png").image
        ).place(x = 140, y = 190)
        
        Label(
            "Current_Label",
            root,
            text = "Current:",
            anchor=tk.W,           
            height=1,              
            width=30,              
            bd=1,                  
            font=("Arial", 10), 
            cursor="hand2",   
            fg="black",                           
            justify = tk.RIGHT,  
            wraplength=100   
            ).place(x = 300, y = 10, width = 80,height = 20)
        Label(
            "Current",
            root,
            textvariable = self.c1,
            anchor=tk.W,           
            height=1,              
            width=30,              
            bd=1,                  
            font=("Arial", 10), 
            cursor="hand2",   
            fg="black",                           
            justify = tk.LEFT,  
            wraplength=100   
            ).place(x = 350, y = 10, width = 80,height = 20)
        Label(
            "T1_Label",
            root,
            text = "T1:",
            anchor=tk.W,           
            height=1,              
            width=30,              
            bd=1,                  
            font=("Arial", 10), 
            cursor="hand2",   
            fg="black",                           
            justify = tk.RIGHT,  
            wraplength=100   
            ).place(x = 300, y = 40, width = 80,height = 20)
        Label(
            "T1",
            root,
            textvariable = self.t1,
            anchor=tk.W,           
            height=1,              
            width=30,              
            bd=1,                  
            font=("Arial", 10), 
            cursor="hand2",   
            fg="black",                           
            justify = tk.LEFT,  
            wraplength=100   
            ).place(x = 350, y = 40, width = 80,height = 20)
        Label(
            "T2_Label",
            root,
            text = "T2:",
            anchor=tk.W,           
            height=1,              
            width=30,              
            bd=1,                  
            font=("Arial", 10), 
            cursor="hand2",   
            fg="black",                           
            justify = tk.RIGHT,  
            wraplength=100   
            ).place(x = 300, y = 70, width = 80,height = 20)
        Label(
            "T2",
            root,
            textvariable = self.t2,
            anchor=tk.W,           
            height=1,              
            width=30,              
            bd=1,                  
            font=("Arial", 10), 
            cursor="hand2",   
            fg="black",                           
            justify = tk.LEFT,  
            wraplength=100   
            ).place(x = 350, y = 70, width = 80,height = 20)
        
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
            ).place(x = 300, y = 100, width = 180,height = 100)
        
        StandardLabel(
            "Status",
            root,
            image = TkImage("status_bad", r"tools\RDT\images\Status_Bad.png").image
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
        self.load_rdt()
        Label.instances["T1"].bind("<Button-1>", self.rdt.update_gui)
        Label.instances["T2"].bind("<Button-1>", self.rdt.update_gui)
        Label.instances["Current"].bind("<Button-1>", self.rdt.update_gui)
    #endregion
    
    #region rdt
    def load_rdt(self):
        self.logger.info("Loading driver")
        self.process_display.set("Loading Driver")
        self.root.update_idletasks()
        try:
            self.rdt = rdt_Driver.NI_RDT(self.root, self.c1, self.t1, self.t2, 
                                         self.T_bias_on, self.t_run, self.t_delay, 
                                         self.fan_delay, self.T_cool, self.num_of_meas, 
                                         self.min_val, self.max_val)
            self.rdt.init_rdt()
        except Exception as e:
            traceback.print_exc()
        if self.rdt.Status:
            StandardLabel(
                "Status",
                self.root,
                image = TkImage("status_Bad",r"tools\RDT\images\Status_Good.png").image,
            ).place(x = 140, y = 120)
            self.logger.info("Driver loaded successfully")
        else:
            StandardLabel(
                "Status",
                self.root,
                image = TkImage("status_bad", r"tools\RDT\images\Status_Bad.png").image
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
        resp = self.tcp.soc.recv(1024).decode()
        
        self.logger.debug(f"Received response: {resp}")
        self.logger.debug("Sending position to server")
        if self.position == "": self.position = "None"
        
        self.tcp.soc.send(self.position.encode())
        self.description = self.tcp.soc.recv(1024).decode()
        
        self.logger.debug(f"got {self.description} from server")
        self.logger.debug("Sending description request to server")

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
            try:
                self.rdt.standard_procedure()
            #     if self.rdt.Status:
            #         try:
            #             self.rdt.measure()
            #             self.value = (sum(self.rdt.values)/len(self.rdt.values)) * 4.517 * 1 * 1.006
            #             if self.connected:
            #                 self.tcp_proptocol()
            #             self.process_display.set("Ready")
            #         except Exception as e:
            #             traceback.print_exc()
            #             self.rdt.Status = False
            #             print("Measuring fail", e)
                data:list[str | int | float] = [self.sample_num, str(dt.now())]
                
                
            #     if not self.connected: #always get a sample description if not connected
            #         self.logger.info("Not connected to server, having user manual enter sample description")
            #         self.wait.set(True)
            #         self.toggle_desc()
            #         self.root.wait_variable(self.wait)
                
                
                
                data.append(self.description)
                data.append(self.position)
                datas = []
                print(self.rdt.t)
                print(self.rdt.C1)
                print(self.rdt.T1)
                print(self.rdt.T2)
                
                i = 0
                for Temp in self.rdt.T1:
                    temp = [d for d in data]
                    new_data = [self.rdt.t[i], self.rdt.C1[i], Temp, self.rdt.T2[i]]
                    for j in new_data:temp.append(j)
                    
                    datas.append(temp)
                    
                    i += 1
                print(datas)
                self.fmanager.write_data("RDT", ["sample id", "time", "desc", "pos" "time of sample", "Current", "T_hotplate", "T_hotplate2"],datas)
                self.rdt.cooldown()
                
            except:
                print("ERROR")
                traceback.print_exc()
                self.rdt.cooldown()
            
            if not self.rdt.Status:
                self.load_rdt()
    #endregion
    

    #region threading
    
        
        
    #endregion
if __name__ == "__main__":
    logging.info("start from main")
    args = iu.get_args_as_dict(sys.argv[2:])
    try:
        SERVER = sys.argv[1]
    except:
        # SERVER = "127.0.0.1" 
        SERVER = "192.168.1.1"
    
    
    PORT = 5050
    ADDR = (
        SERVER, 
        PORT
        )
    print(args)
    temp = rdt_app(
            SERVER, 
            PORT,
            T_bias_on = float(args["T_bias_on"]) if "T_bias_on" in list(args.keys()) else 20.0, #should be 150
            t_run = float(args["t_run"]) if "t_run" in list(args.keys()) else 1.0,
            t_delay = float(args["t_delay"]) if "t_delay" in list(args.keys()) else 1.0,
            fan_delay = float(args["fan_delay"]) if "fan_delay" in list(args.keys()) else 30.0,
            T_cool = float(args["T_cool"]) if "T_cooldown" in list(args.keys()) else 30.0,
            num_of_meas = float(args["num_of_meas"]) if "num_of_meas" in list(args.keys()) else 60.0,
            min_val = float(args["Min_val"]) if "Min_val" in list(args.keys()) else -0.05,
            max_val = float(args["Max_val"]) if "Max_val" in list(args.keys()) else 0.05,
            )
    temp.startApp()

 
