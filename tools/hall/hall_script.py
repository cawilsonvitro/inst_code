#encoding=<UTF-8>
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
                print("PLease enter a sample number")
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
                    # self.client = iu.client(self.ip, self.port) 
                # self.client.connect()
                # self.client.id()
                # self.starApp()
                # for file in new_files:
                #     # print(file)
                #     path = os.path.join("data", file)
                #     self.client.soc.send("MEAS".encode())
                #     resp = self.client.soc.recv(1024).decode()
                #     self.client.soc.send(self.sample_num.encode())
                #     resp = self.client.soc.recv(1024).decode()
                #     _,data = iu.parse(path)
                #     data_str = (",").join(data)
                    
                #     self.client.soc.send(data_str.encode())
                    
                    
                # self.client.disconnect()
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
    
    temp = silent_hall(SERVER, PORT)
    temp.state_sys()

