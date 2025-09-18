#encoding=<UTF-8>
#region Imports
import sys
import os
from instutil import inst_util as iu
import sys
from gui_package_cawilvitro import *
import tkinter as tk
#endregion 


import sys
import os

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
        
    
    #region gui
    def starApp(self):
        self.root = tk.Tk()
        self.root.title("Hall Effect measurement")
        self.root.geometry("240x240")
        self.root.resizable(width=False,height=False)
        self.root.bind("<Escape>", self.endApp)
        self.root.protocol("WM_DELETE_WINDOW",self.endProto)
        self.process_display = tk.StringVar() 
        self.process_display.set("Booting")
        self.root.update_idletasks()
        self.buildGUI(self.root)
        
        self.root.mainloop()
    
    #region GUI 
    
       
        
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
        dropdown.remove(None)
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
        
    #endregion
    
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
            self.root.quit()
        
            
    #endregion
    
    
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
        new_files = []
        for time in times:
            if float(time) > pre_file:
                new_files.append(all_files[i])
            i += 1
            
        print(new_files)
        
        # print(new_files)
        if len(new_files) != 0:
            try:
                self.client = iu.client(self.ip, self.port) 
                self.client.connect()
                self.client.id()
                self.starApp()
                for file in new_files:
                    # print(file)
                    path = os.path.join("data", file)
                    self.client.soc.send("MEAS".encode())
                    resp = self.client.soc.recv(1024).decode()
                    self.client.soc.send(self.sample_num.encode())
                    resp = self.client.soc.recv(1024).decode()
                    _,data = iu.parse(path)
                    data_str = (",").join(data)
                    
                    self.client.soc.send(data_str.encode())
                    
                    
                self.client.disconnect()
                raise Exception
                with open(self.tracker, "r") as f:lines=f.readlines()
                
                lines[1] = "True"
                
                with open(self.tracker, "w") as f: f.writelines(lines)
                
            except:
                with open(self.tracker, "r") as f:lines=f.readlines()
                
                lines[1] = "False"
                
                with open(self.tracker, "w") as f: f.writelines(lines)
                
            
            
            
        else:
            print("No new files detected")



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

