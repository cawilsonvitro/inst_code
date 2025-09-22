#encoding=<UTF-8>
#region Imports
import sys
import os
from instutil import inst_util as iu
import sys
from gui_package_cawilvitro import *
import tkinter as tk
from functools import partial
# import logging
# from logging.handlers import TimedRotatingFileHandler
from datetime import datetime as dt
import traceback
#endregion 

#region logging
# date = dt.now().strftime("%m-%d-%Y, Hour %H Min %M Sec %S")

# logging.basicConfig(
#     level=logging.DEBUG, # Set a global logging level
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         # logging.StreamHandler(), # Log to console
#         TimedRotatingFileHandler(f'tools\\hall\\logs\\{date}.log', when = "D", backupCount= 5)
#     ]
# )

#endregion 

cwd = os.getcwd()

def get_exe_location():
    """
    Returns the absolute path to the compiled executable.
    """
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        return os.path.dirname(sys.executable)
    else:
        # Running as a regular Python script
        return os.path.dirname(os.path.abspath(__file__))

exe_path = get_exe_location()
print(f"The executable is located at: {exe_path}, current working path is {cwd}")

if str(cwd).lower() != str(exe_path).lower():
    os.chdir(exe_path)
    print(f"Changed working directory to: {os.getcwd()}")

class silent_hall:
    '''
    A class to manage Hall Effect measurement workflow, including GUI interaction,
    file tracking, and TCP communication with a remote server.
    Attributes:
        ip (str): IP address for TCP connection.
        port (int): Port for TCP connection.
        tracker (str): Path to the tracker file for state management.
        hms (str): Directory containing measurement data files.
        cwd (str): Current working directory.
        logger (logging.Logger): Logger instance for the class.
        position (str): Selected position from GUI.
        root (tk.Tk): Tkinter root window for GUI.
        process_display (tk.StringVar): StringVar for process status display.
        wait (tk.BooleanVar): BooleanVar for GUI state.
        sample_num (str): Selected sample number from GUI.
        description (str): Sample description from GUI.
        id (str): Sample ID from GUI.
        value (str): Parsed measurement data.
        new_files (list): List of newly detected files.
        tcp (iu.client): TCP client instance.
        current_file (str): Currently processed file.
        
    Methods:
        __init__(ip, port, tracker="script_tracker.txt", hmsdata="data"):
            Initializes the silent_hall instance with connection and file tracking parameters.
        starApp():
            Launches the GUI application for Hall Effect measurement.
        update():
            Updates the sample dropdown list in the GUI by querying the server.
        get_pos(event):
            Retrieves the selected position from the GUI dropdown.
        buildGUI(root):
            Constructs the GUI layout and widgets.
        callback(eventObject):
            Handles sample selection events and ends the application.
        endProto():
            Wrapper to end the application via protocol.
        endApp(event):
            Ends the application, collects user input, and initiates TCP protocol.
        state_sys():
            Manages state tracking using a tracker file, detects new measurement files,
            and launches the GUI for each new file.
        tcp_protocol():
            Handles the TCP communication protocol for sending measurement metadata and data to the server.
    '''
    def __init__(self, ip, port, 
                 tracker = "script_tracker.txt",
                 hmsdata = "data"
                 ):

        
        self.position = ""



        self.ip = ip
        self.port = port
        self.tracker = tracker
        self.hms = hmsdata
        self.cwd = os.getcwd()
        
        #logging

        class_name = str(type(self))
        name = class_name.split(" ")[-1][:-1].replace("'", "")
        
        # self.logger = logging.getLogger(name)
        
        # #self.logger.info("hall script started")
    
    #region gui
    def starApp(self):
        # #self.logger.info("Starting GUI application")
        self.root = tk.Tk()
        self.root.title(self.current_file)
        self.root.geometry("300x500")
        self.root.resizable(width=False,height=False)
        self.root.bind("<Escape>", self.endApp)
        self.root.protocol("WM_DELETE_WINDOW",self.endProto)
        self.process_display = tk.StringVar() 
        self.process_display.set("Booting")
        self.root.update_idletasks()
        self.buildGUI(self.root)
        # #self.logger.info("GUI built successfully, entering main loop")
        self.root.mainloop()

    def update(self) -> None:
        # #self.logger.info("Updating sample dropdown")
        self.tcp.soc.send("UPDATE".encode())
        resp:str = self.tcp.soc.recv(1024).decode()
        print(resp)
        if resp != "None":
            dropdown.instances["samples"].configure(values=resp.split(","))
        else:
            dropdown.instances["samples"].configure(values=[])
    
    def get_pos(self,event) -> None:        
        #self.logger.debug("Getting pos")
        self.position = "" 
        self.position = dropdown.instances["position"].get()
        #self.logger.debug(f"{self.position} selected")
    
    def buildGUI(self, root):
        """_summary_ builds gui

        Args:
            root (_type_): tk root
        """
        
                #to track our var
        self.wait:tk.BooleanVar = tk.BooleanVar()
        
        self.wait.set(False)
        
        
        dropdown.remove(None)
        Label.remove(None)
        TextBox.remove(None)
        
        dropdown(
            "samples",
            root,
            values = "",
            width = 28,
            postcommand=self.update
        ).place(x = 5, y = 20)
        dropdown.instances["samples"].bind("<<ComboboxSelected>>",self.callback) #DO NEED THIS

        dropdown(
            "position",
            root,
            values = ["LT", "LC", "LL", "CT", "CC", "CL", "RT", "RC", "RL"],
            width = 5,
        ).place(x = 5, y = 80)
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
            ).place(x = 5, y = 60, width = 80,height = 20)
        
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
            ).place(x = 5, y = 0, width = 80,height = 20)
        
        Label(
            "desc_label",
            root,
            text = "Description:",
            anchor=tk.W,           
            height=1,              
            width=30,              
            bd=1,                  
            font=("Arial", 10), 
            cursor="hand2",   
            fg="black",                           
            justify = tk.LEFT,  
            wraplength=100   
            ).place(x = 5, y = 160, width = 80,height = 20)
        
        TextBox("desc", root, height = 20, width = 20, ).place(x = 5, y = 180)
        
        Label(
            "id_label",
            root,
            text = "ID:",
            anchor=tk.W,           
            height=1,              
            width=30,              
            bd=1,                  
            font=("Arial", 10), 
            cursor="hand2",   
            fg="black",                           
            justify = tk.LEFT,  
            wraplength=100   
            ).place(x = 5, y = 110, width = 80,height = 20)
        
        TextBox("id", root, height = 1, width = 20, ).place(x = 5, y = 130)

        
    def callback(self, eventObject):
        self.endApp(None)
    
    def endProto(self):
        '''
        wrapper to endApp
        '''
        self.endApp(None)
    
    def endApp(self, event):
        '''
        ends application
        '''
        #self.logger.info("Ending application")
        self.quit = True
        self.sample_num = dropdown.instances["samples"].get()
        if self.sample_num == "":
                print("Please enter a sample number")
                #self.logger.warning("No sample number entered, waiting for user input")
        else:
            #self.logger.info(f"Sample number {self.sample_num} selected, getting meta data then writing output")
            self.description = TextBox.instances["desc"].get("1.0", "end-1c")
            self.id = TextBox.instances["id"].get("1.0", "end-1c")    
            col, data = iu.parse(os.path.join(os.getcwd(),'data', self.current_file))
            print(col)
            self.value = (",").join(data)
            self.tcp_protocol()
            print(len(col), len(data))
            self.root.quit()
        
            
    #endregion
    
#region state system  
    def state_sys(self):
        """
            uses a txt file to keep track of number of files before and
            after launch
        """
        
        # #self.logger.info("Starting state system")
        files:int = 0 #number of files
        all_files: list[str] = []
        
        for dirpath,_,filenames in os.walk(self.hms):
            for f in filenames:
                if ".txt" in f:
                    all_files.append(f)

        with open(self.tracker, "r") as f:lines = f.readlines()
            
        if lines[1].strip().lower() == 'false':
            update:bool = False
        elif lines[1].strip().lower() == 'true':
            update:bool = True
        #update is to check if the last run was good. If it was
        os.system("\"C:\\Program Files (x86)\\HMS3000 V3.52\\HMS-3000 V3.52.exe\"")
        
        all_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.hms, x)))
        timesorted = [os.path.getmtime(os.path.join(self.hms, f)) for f in all_files]
        recent = timesorted[-1]
      #  if self.state == "post":
        pre_file: float = float(lines[0].strip())

        all_files = os.listdir(self.hms)
        all_files = [f for f in all_files if ".txt" in f]
        times = [os.path.getmtime(os.path.join(self.hms, f)) for f in all_files]
        times.sort()
        self.new_files = []
        self.new_files = [i for i in all_files if os.path.getmtime(os.path.join(self.hms, i)) > pre_file and ".txt" in i]
        # i:int = 0
        # for time in times:
        #     if float(time) > pre_file:
        #         if ".txt" in all_files[i]:self.new_files.append(all_files[i])
        #     i += 1
            
        print(self.new_files)
        
        # print(new_files)
        if len(self.new_files) != 0:
            try:
                self.tcp = iu.client(self.ip, self.port) 
                self.tcp.connect()
                self.tcp.id()
                for file in self.new_files:
                    self.current_file = file
                    self.starApp()
                    # raise Exception #this is to prevent new file from being marked as read, please comment to run normally
                    with open(self.tracker, "r") as f:lines=f.readlines()
                    
                lines[0] = str(recent) + "\n"
                lines[1] = "True"
                
                with open(self.tracker, "w") as f: f.writelines(lines)
                self.tcp.disconnect()
            except:
                print(traceback.format_exc())
                with open(self.tracker, "r") as f:lines=f.readlines()
                
                lines[1] = "False"
                
                with open(self.tracker, "w") as f: f.writelines(lines)
            try: 
                self.tcp.disconnect()
            except AttributeError:
                print("tcp client not created, cannot disconnect")
                #self.logger.error("tcp client not created, cannot disconnect")
        else:
            print("No new files detected")
            lines = [str(recent) + "\n", str(update)]
            with open(self.tracker, "w") as f:f.writelines(lines)

    def tcp_protocol(self):
        
        #self.logger.info("Starting TCP protocol")
        
        #self.logger.debug("Sending META command to server")
        
        self.tcp.soc.send("META".encode())
        resp = self.tcp.soc.recv(1024).decode()
        
        #self.logger.debug(f"Received response: {resp}")
        #self.logger.debug("Sending sample number to server")
        
        self.tcp.soc.send(str(self.sample_num).encode())
        resp = self.tcp.soc.recv(1024).decode()
        
        #self.logger.debug(f"Received response: {resp}")
        #self.logger.debug("Sending position to server")
        if self.position == "": self.position = "None"
        
        self.tcp.soc.send(self.position.encode())
        self.description = self.tcp.soc.recv(1024).decode()
        
        #self.logger.debug(f"got {self.description} from server")
        #self.logger.debug("Sending description request to server")

        #self.logger.debug(f"user set description to {self.description}")

        #self.logger.info("Starting TCP MEAS protocol")

        #self.logger.debug("Sending MEAS command")
        
        self.tcp.soc.send("MEAS".encode())
        
        resp = self.tcp.soc.recv(1024).decode()
        #self.logger.debug(f"got {resp} from Server")
        #self.logger.debug(f"sending sample id {self.sample_num}")
        
        self.tcp.soc.send(self.sample_num.encode())
        resp = self.tcp.soc.recv(1024).decode()
        
        #self.logger.debug(f"Received response: {resp}")
        
        self.tcp.soc.send(self.description.encode())
        resp = self.tcp.soc.recv(1024).decode()
        
        #self.logger.debug(f"Received response: {resp}")

        self.tcp.soc.send(self.value.encode())
        print(self.value.encode())
        resp = self.tcp.soc.recv(1024).decode()
        
        #self.logger.debug(f"Received response: {resp}")
        if resp != "data received":
            print(f"unexpected response from server {resp}")
           #self.logger.error(f"unexpected response from server {resp}")
        else:
            print("data sent successfully")
            #self.logger.info("TCP protocol complete")
    #endregion


if __name__ == "__main__":
        #SERVER = "127.0.0.1" 
    try:
        SERVER = sys.argv[1]
    except:
        SERVER = "192.168.1.1"
    PORT = 5050
    cwd = os.getcwd()
    if str(cwd).lower() != str(exe_path).lower():
        os.chdir(exe_path)
        print(f"Changed working directory to: {os.getcwd()}")
    
    temp = silent_hall(SERVER, PORT)
    temp.state_sys()

