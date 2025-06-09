#region imports
from gui_package_cawilvitro import *
import fourpp as fourpp
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


class four_point_app():
    
    #region application start up
    def __init__(self, ip, port):
        '''
        init class for use
        '''
        self.quit = False
        self.process_display = None

        #siglent
        self.DM = None
        self.resource_string = "USB0::0xF4EC::0x1208::SDM36HCD801150::INSTR"

        #data management
        self.value = None
        self.dataPath = r"data/"
        self.sample_num = 1
        self.exst = ".csv"
        
        #threading
        # self.message: Queue[Any] = Queue(maxsize=1)
        # self.response: Queue[Any] = Queue(maxsize=1)
        
        
        #tcp handels init too
        self.tcp = tcp_client.client(ip, port)#, self.message, self.response)
        self.tcp.connect()
        self.tcp.id() #tells server the ip is connected
    
    def startApp(self):
        self.root = tk.Tk()
        self.root.title("4 point probe measurement")
        self.root.geometry("480x240")
        self.root.resizable(width=False,height=False)
        self.root.bind("<Escape>", self.endApp)
        self.root.protocol("WM_DELETE_WINDOW",self.endProto)
        self.process_display = tk.StringVar() 
        self.process_display.set("Booting")
        self.root.update_idletasks()
        self.buildGUI(self.root)
        
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
        self.DM.quit()
        self.root.quit()
        
    #endregion
   
    #region building GUI
    def buildGUI(self, root):
        '''
        builds gui for user interaction
        '''
        Button.remove(None)
        Label.remove(None)
        StandardLabel.remove(None)
        
        StandardButtons(
            "Measure",
            root,
            image = TkImage("Measure", r"tools\fourpp\images\Measure_Button.png").image,
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
            image = TkImage("status_bad", r"tools\fourpp\images\Status_Bad.png").image
        ).place(x = 140, y = 120)
        
        self.process_display.set("GUI Built, initalizing DM")
        self.load_dm()

    #endregion
    
    #region 4 pp
    def load_dm(self):
        try:
            self.DM = fourpp.siglent(self.resource_string)
            self.DM.init_driver()
        except Exception as e:
            print(e)
        if self.DM.status:
            StandardLabel(
                "Status",
                self.root,
                image = TkImage("status_Bad",r"tools\fourpp\images\Status_Good.png").image,
            ).place(x = 140, y = 120)
        else:
            StandardLabel(
                "Status",
                self.root,
                image = TkImage("status_bad", r"tools\fourpp\images\Status_Bad.png").image
            ).place(x = 140, y = 120)
    
    def measure(self):
        if self.DM.status:
            try:
                self.DM.measure()
                print(self.DM.values)
                self.value = (sum(self.DM.values)/len(self.DM.values)) * 4.517 * 1 * 1.006
                
                
                self.tcp.soc.send("MEAS".encode())
                self.tcp.soc.send(str(self.value).encode())
                
                resp = self.tcp.soc.recv(1024).decode()

                if resp != "data received":
                    print("ERROR")

                    
                # self.message.put(self.value)
            except Exception as e:
                self.DM.status = False
                print("Measuring fail", e)

        if not self.DM.status:
            self.load_dm()
    #endregion
    

    #region threading
    
        
        
    #endregion
if __name__ == "__main__":
    
    #SERVER = "127.0.0.1" #"192.168.1.1"
    SERVER = "192.168.1.1"
    PORT = 5050
    ADDR = (SERVER, PORT)
    
    temp = four_point_app(SERVER, PORT)
    temp.startApp()

 