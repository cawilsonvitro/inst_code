#encoding=<UTF-8>
#region Imports
import sys
import os
from instutil import inst_util as iu
import sys
from gui_package_cawilvitro import *
import tkinter as tk
from functools import partial
import sys
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime as dt
import traceback
#endregion 

#region logging
date = dt.now().strftime("%m-%d-%Y, Hour %H Min %M Sec %S")

logging.basicConfig(
    level=logging.DEBUG, # Set a global logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.StreamHandler(), # Log to console
        TimedRotatingFileHandler(f'tools\\hall\\logs\\{date}.log', when = "D", backupCount= 5)
    ]
)

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
    
    def __init__(self, ip, port, 
                 tracker = "script_tracker.txt",
                 hmsdata = "data"
                 ):

        self.ip = ip
        self.port = port
        self.tracker = tracker
        self.hms = hmsdata
        self.cwd = os.getcwd()
        
                #logging

        class_name = str(type(self))
        name = class_name.split(" ")[-1][:-1].replace("'", "")
        
        self.logger = logging.getLogger(name)
        
        self.logger.info("4 point probe app initialized")
    
    #region gui
    def starApp(self):
        self.root = tk.Tk()
        self.root.title("Hall Effect measurement")
        self.root.geometry("800x800")
        self.root.resizable(width=False,height=False)
        self.root.bind("<Escape>", self.endApp)
        self.root.protocol("WM_DELETE_WINDOW",self.endProto)
        self.process_display = tk.StringVar() 
        self.process_display.set("Booting")
        self.root.update_idletasks()
        self.buildGUI(self.root)
        
        self.root.mainloop()

    def update(self) -> None:
        self.logger.info("Updating sample dropdown")
        self.tcp.soc.send("UPDATE".encode())
        resp:str = self.tcp.soc.recv(1024).decode()
        print(resp)
        if resp != "None":
            dropdown.instances["samples"].configure(values=resp.split(","))
        else:
            dropdown.instances["samples"].configure(values=[])
    
    def toggle_id(self):
        self.logger.info("Toggling ID Window")
        state = self.id_window.state()
        if state == "normal":self.id_window.withdraw()
        if state == "withdrawn":self.id_window.deiconify()
        
    def get_id(self, event) -> None:
        self.logger.debug("Getting ID")
        self.id = TextBox.instances["id"].get("1.0","end-1c")
        print(self.id)
        TextBox.instances["id"].delete("1.0","end-1c")
        self.toggle_id()
    
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
        ).place(x = 0, y = 60)
        # dropdown.instances["samples"].bind("<<ComboboxSelected>>",self.callback) dont need this

        dropdown(
            "position",
            root,
            values = ["LT", "LC", "LL", "CT", "CC", "CL", "RT", "RC", "RL"],
            width = 5,
        ).place(x = 0, y = 120)
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
            ).place(x = 0, y = 100, width = 80,height = 20)
        
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
        
        
        TextBox("desc", root, height = 20, width = 20, ).place(x = 400, y = 400)
        
        
        
        # #description window
        # TextBox.remove(None) #here so we only have to call this once might havet to switch
        # self.desc_window = tk.Toplevel(self.root)
        # self.desc_window.geometry("300x800")
        # self.desc_window.title("Sample Description")
        # self.desc_window.bind('<Escape>', self.get_desc)
        # self.desc_window.protocol("WM_DELETE_WINDOW", partial(self.get_desc, None))
        # TextBox("desc", self.desc_window, height = 20, width = 32).place(x = 10, y = 50)
        # self.desc_window.withdraw()
        
        # #operator id window
        # self.id_window = tk.Toplevel(self.root)
        # self.id_window.geometry("300x300")
        # self.id_window.title("Operator ID")
        # self.id_window.bind('<Escape>', self.get_id)
        # self.id_window.protocol("WM_DELETE_WINDOW", partial(self.get_id, None))
        # TextBox("id", self.id_window, height = 2, width = 30).place(x = 10, y = 50)
        # Label(
        #     "Operator_ID",
        #     self.id_window,
        #     text = "Operator ID:",
        #     anchor=tk.W,           
        #     height=1,              
        #     width=30,              
        #     bd=1,                  
        #     font=("Arial", 10), 
        #     cursor="hand2",   
        #     fg="black",                           
        #     justify = tk.LEFT,  
        #     wraplength=100   
        #     ).place(x = 0, y = 30, width = 80,height = 20)
        # self.id_window.withdraw()
        
    def callback(self, eventObject):
        self.endApp(None)

    def update(self) -> None:
        # print("asking")
        self.client.soc.send("UPDATE".encode())
        resp:str = self.client.soc.recv(1024).decode()
        # print(resp)
        if resp != "None":
            dropdown.instances["samples"].configure(values=resp.split(","))
        else:
            dropdown.instances["samples"].configure(values=[])
        #debugging
        
    def endProto(self):
        '''
        wrapper to endApp
        '''
        self.endApp(None)
    
    def endApp(self, event):
        '''
        ends application
        '''
        self.quit = True
        self.sample_num = dropdown.instances["samples"].get()
        if self.sample_num == "":
                print("Please enter a sample number")
        else:
            for file in self.new_files:
                print(file)
                self.measure(file)
                
            self.root.quit()
        
            
    #endregion
    
#region state system  
    def state_sys(self):
        """
            uses a txt file to keep track of number of files before and
            after launch
        """
        
    
        files:int = 0 #number of files
        all_files: list[str] = []
        
        for dirpath,_,filenames in os.walk(self.hms):
            for f in filenames:all_files.append(f)
            
        all_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.hms, x)))
        timesorted = [os.path.getmtime(os.path.join(self.hms, f)) for f in all_files]
        recent = timesorted[-1]
        
        with open(self.tracker, "r") as f:lines = f.readlines()
            
        if lines[1].strip().lower() == 'false':
            update:bool = False
        elif lines[1].strip().lower() == 'true':
            update:bool = True
        
        if update:
            with open(self.tracker, "w") as f:f.write(str(recent))
        os.system("\"C:\\Program Files (x86)\\HMS3000 V3.52\\HMS-3000 V3.52.exe\"")
      #  if self.state == "post":
        pre_file: float = float(lines[0].strip())
        # files:int = 0
        # for dirpath,_,filenames in os.walk(self.hms):
        #     for f in filenames:
        #         files += 1
        # new_files:int = files - pre_file

        all_files = os.listdir(self.hms)
        times = [os.path.getmtime(os.path.join(self.hms, f)) for f in all_files]
        times.sort()
        
        i:int = 0
        self.new_files = []
        for time in times:
            if float(time) > pre_file:
                self.new_files.append(all_files[i])
            i += 1
            
        print(self.new_files)
        
        # print(new_files)
        if len(self.new_files) != 0:
            try:
                self.client = iu.client(self.ip, self.port) 
                self.client.connect()
                self.client.id()
                for file in self.new_files:
                    self.current_file = file
                    self.starApp()
                
            
     
                self.client.disconnect()
                raise Exception #this is to prevent new file from being marked as read, please comment to run normally
                with open(self.tracker, "r") as f:lines=f.readlines()
                
                lines[1] = "True"
                
                with open(self.tracker, "w") as f: f.writelines(lines)
                
            except:
                
                print(traceback.format_exc())
                with open(self.tracker, "r") as f:lines=f.readlines()
                
                lines[1] = "False"
                
                with open(self.tracker, "w") as f: f.writelines(lines)
                
            
            
            
        else:
            print("No new files detected")

    def measure(self, file):
        self.desc_window.title(f"Description for {file}")
        self.id_window.title(f"Operator ID for {file}")
        
        
        # path = os.path.join("data", file)
        print("I RAN 1")
        self.wait.set(True)
        self.toggle_id()
        self.root.wait_variable(self.wait)
        print("I ran 3")
        
        self.wait.set(True)
        self.toggle_desc()
        self.root.wait_variable(self.wait)
        print("I RAN 2")
    
    def tcp_protocol(self, path):
        
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
        self.toggle_id()
        self.root.wait_variable(self.wait)
            
        
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
           self.logger.error(f"unexpected response from server {resp}")
        else:
            self.logger.info("TCP protocol complete")
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

