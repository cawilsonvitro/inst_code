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
    def __init__(self, ip, port, 
                 tracker = "script_tracker.txt",
                 hmsdata = "data"
                 ):

        
        self.position = ""


        print(type(ip))
        self.ip = ip
        self.port = port
        self.tracker = tracker
        self.hms = hmsdata
        self.cwd = os.getcwd()
        
        #Input form
        self.sample_num = ""
        self.position = ""
        self.ID = ""
        self.description = ""
    #region testing

    def sql_setup(self):
        cwd = os.getcwd().split("\\")[:-2]
        cwd.append("config.json")
        self.config_path = "\\".join(cwd)
        self.SQL = iu.sql_client(self.config_path)
        self.SQL.load_config()
        self.SQL.connect()
        
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
        pre_file: float = float(lines[0].strip())

        all_files = os.listdir(self.hms)
        all_files = [f for f in all_files if ".txt" in f]
        times = [os.path.getmtime(os.path.join(self.hms, f)) for f in all_files]
        times.sort()
        self.new_files = []
        self.new_files = [i for i in all_files if os.path.getmtime(os.path.join(self.hms, i)) > pre_file and ".txt" in i]

            
        print(self.new_files)
        
        # print(new_files)
        if len(self.new_files) != 0:
            try:
                for file in self.new_files:
                    self.current_file = file
                    # self.startApp()
                    self.sample_num = input("Enter Sample Number: ")
                    self.position = input("Enter Position: ")
                    if self.position == "": self.position = "None"
                    self.description = input("Enter Description: ")
                    self.id = input("Enter ID: ")
                    col, data = iu.parse(os.path.join(os.getcwd(),'data', self.current_file))
                    sql_val = []
                    i = 0
                    for d in data:
                        sql_val.append([col[i], d])
                        i += 1
                    sql_val.append(["ha_sample_id", self.sample_num])
                    sql_val.append(["ha_pos", self.position])
                    sql_val.append(["ha_description", self.description])
                    sql_val.append(["ha_time", dt.now().strftime("%m-%d-%Y, Hour %H Min %M Sec %S")])
                    self.SQL.check_columns("hall", (",").join(col))
                    self.SQL.write("hall", sql_val)

                    
                    # raise Exception #this is to prevent new file from being marked as read, please comment to run normally
                    with open(self.tracker, "r") as f:lines=f.readlines()
                    
                lines[0] = str(recent) + "\n"
                lines[1] = "True"
                
                with open(self.tracker, "w") as f: f.writelines(lines)
            except:
                print(traceback.format_exc())
                with open(self.tracker, "r") as f:lines=f.readlines()
                
                lines[1] = "False"
                
                with open(self.tracker, "w") as f: f.writelines(lines)
            try: 
                pass
            except AttributeError:
                print("tcp client not created, cannot disconnect")
        else:
            print("No new files detected")
            lines = [str(pre_file) + "\n", str(update)] #do not change the file if no new files
            with open(self.tracker, "w") as f:f.writelines(lines)

    #endregion


if __name__ == "__main__":
        #SERVER = "127.0.0.1" 

    
    cwd = os.getcwd()
    if str(cwd).lower() != str(exe_path).lower():
        os.chdir(exe_path)
        print(f"Changed working directory to: {os.getcwd()}")
    
    temp = silent_hall("0", 0)
    temp.sql_setup()
    temp.state_sys()

