#region Imports
import time
import sys
import os
from instutil import inst_util as iu
import sys
from gui_package_cawilvitro import *
import tkinter as tk
#endregion 


class silent_hall:
    
    def __init__(self, ip, port, 
                 tracker = "script_tracker.txt",
                 hmsdata = "data"
                 ):
        """_summary_ for HMS 3000 silent running, will connect to tcp server and run in back
        round for code

        Args:
            ip (_type_): ip for tcp server
            port (_type_): port for tcp server.
        Sys Args:
            <ip of server> <state of hms> s
        """
        self.ip = ip
        self.port = port
        self.tracker = tracker
        self.hms = hmsdata
        self.state = sys.argv[2]
        self.cwd = os.getcwd()
        
        self.state_sys()
    
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
        dropdown.instances["samples"].bind("<<ComboboxSelected>>",self.callback)
    
    
    def callback(self, eventObject):
        self.endApp(None)

    def update(self) -> None:
        print("asking")
        self.client.soc.send("UPDATE".encode())
        resp:str = self.client.soc.recv(1024).decode()
        print(resp)
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
                print("PLease enter a sample number")
        else:
            self.root.quit()
        
            
    #endregion
    
    
    def state_sys(self):
        """
            uses a txt file to keep track of number of files before and
            after launch
        """
        if self.state == "pre":
            files:int = 0
            for dirpath,_,filenames in os.walk(self.hms):
                for f in filenames:
                    files += 1

            with open(self.tracker, "w") as f:
                f.write(str(files))

        if self.state == "post":
            pre_file: int
            
            with open(self.tracker, "+r") as f:
                pre_file = int(f.read())
            files:int = 0
            for dirpath,_,filenames in os.walk(self.hms):
                for f in filenames:
                    files += 1
            new_files:int = files - pre_file

            all_files = os.listdir(self.hms)
            all_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.hms, x)))
            if new_files != 0:
                new_files = all_files[-new_files:]
            self.client = iu.client(self.ip, self.port)
            self.client.connect()
            self.client.id()
            self.starApp()
            
            for file in new_files:
                path = os.path.join("data", file)
                self.client.soc.send("MEAS".encode())
                resp = self.client.soc.recv(1024).decode()
                self.client.soc.send(self.sample_num.encode())
                resp = self.client.soc.recv(1024).decode()
                _,data = iu.parse(path)
                data_str = (",").join(data)
                
                self.client.soc.send(data)
                
                
            self.client.disconnect()




if __name__ == "__main__":
        #SERVER = "127.0.0.1" 
    try:
        SERVER = sys.argv[1]
    except:
        SERVER = "192.168.1.1"
    PORT = 5050
    ADDR = (SERVER, PORT)
    
    temp = silent_hall(SERVER, PORT)

