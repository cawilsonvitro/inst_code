#region imports
from gui_package_cawilvitro import *
import nearir as IR
import tkinter as tk
from tkinter import Misc
import tkinter.ttk as ttk
from multiprocessing import Process, Queue
from queue import Empty
import time
import json
import sys
import threading
import tcp_client

#endregion


class near_ir_app():
    
    #region application start up
    def __init__(self, ip, port):
        '''
        init class for use
        '''
        self.quit = False
        self.process_display = None


        #data management
        self.value = None
        self.dataPath = r"data/"
        self.sample_num = 1
        self.exst = ".csv"
        
        #spectrometer
        self.spectrometer = None
        
        #threading
        # self.message: Queue[Any] = Queue(maxsize=1)
        # self.response: Queue[Any] = Queue(maxsize=1)
        
        
        # tcp handels init too
        self.tcp = tcp_client.client(ip, port)#, self.message, self.response)
        self.tcp.connect()
        self.tcp.id() #tells server the ip is connected
    
    def startApp(self):
        self.root = tk.Tk()
        self.root.title("Near IR measurement")
        self.root.geometry("480x240")
        self.root.resizable(width=False,height=False)
        self.root.bind("<Escape>", self.endApp)
        self.root.protocol("WM_DELETE_WINDOW",self.endProto)
        self.process_display = tk.StringVar() 
        self.process_display.set("Booting")
        self.root.update_idletasks()
        self.buildGUI(self.root)
        self.spec_init()
        
        self.root.mainloop()
    
    #endregion
    
    #region app control  
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
        self.tcp.disconnect()
        self.root.quit()
        
    #endregion
   
    #region building GUI
    def update(self) -> None:
        print("asking")
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
        Button.remove(None)
        Label.remove(None)
        StandardLabel.remove(None)
        dropdown.remove(None)
        
        dropdown(
            "samples",
            root,
            values = "",
            width = 28,
            postcommand=self.update,
        ).place(x = 0, y = 60)
        
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
        
        self.process_display.set("GUI Built, initalizing DM")
        
    #endregion
    
    #region spectrometer
    def spec_init(self):
        '''
        initializes spectrometer
        '''
        self.process_display.set("Initializing Spectrometer")
        self.spectrometer = IR.stellarnet(int_time=1000, scans_to_avg=1, x_smooth=0, x_timing=3)
        self.spectrometer.init_driver()
        
        if self.spectrometer.status:
            self.process_display.set("Spectrometer initialized")
            StandardLabel(
                "Status",
                self.root,
                image = TkImage("status_good", r"tools\nearir\images\Status_Good.png").image
            ).place(x = 140, y = 120)
        else:
            self.process_display.set("Spectrometer failed to initialize")
            StandardLabel(
                "Status",
                self.root,
                image = TkImage("status_bad", r"tools\nearir\images\Status_Bad.png").image
            ).place(x = 140, y = 120)
    
    #region data aquisition and processing
    def measure(self):
        self.process_display.set("measuring")
        self.root.update_idletasks()
        self.sample_num = dropdown.instances["samples"].get()
        if self.sample_num == "":
            self.process_display.set("Please select or enter a sample ID")
        else:
            if self.spectrometer.status:
                self.spectrometer.measure()
            else:
                self.spec_init()
            wvs: str = ""
            spec: str = ""
            i: int = 0
            for wv in self.spectrometer.wv:
                wvs += str(wv[0]) + ","
                spec += str(self.spectrometer.spectra[i]) + ","
                i += 1

            wvs = wvs[:-1]
            spec = spec[:-1]
            self.process_display.set("Measuring Done")  


            self.process_display.set("sending data")
            self.root.update_idletasks()

            self.tcp.soc.send("MEAS".encode())
            resp = self.tcp.soc.recv(1024).decode()
            print(resp)
            self.tcp.soc.send(str(self.sample_num).encode())
            resp = self.tcp.soc.recv(1024).decode()
            print(resp)
            self.tcp.soc.send(wvs.encode())
            resp = self.tcp.soc.recv(1024).decode()
            print(resp)
            # self.tcp.soc.send(spec.encode())
            # resp = self.tcp.soc.recv(1024).decode()
            # print(resp)
            
            if resp != "data received":
                print(resp)
                self.process_display.set("ERROR")
            else:
                self.process_display.set("Done")
    
    #endregion
    #region threading
    
        
        
    #endregion
if __name__ == "__main__":
    #SERVER = "127.0.0.1" 
    try:
        SERVER = sys.argv[1]
    except:
        SERVER = "192.168.1.1"
        
    PORT = 5050
    ADDR = (SERVER, PORT)
    
    temp = near_ir_app(SERVER, PORT)
    temp.startApp()

 