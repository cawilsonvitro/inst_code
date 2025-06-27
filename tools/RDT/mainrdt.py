#region imports
from gui_package_cawilvitro import *
import RDT_dummy as rdt
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


class rdt_app():
    
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
        
        #threading
        # self.message: Queue[Any] = Queue(maxsize=1)
        # self.response: Queue[Any] = Queue(maxsize=1)
        
        
        #tcp handels init too
        # self.tcp = tcp_client.client(ip, port)#, self.message, self.response)
        # self.tcp.connect()
        # self.tcp.id() #tells server the ip is connected
    
    def startApp(self):
        self.root = tk.Tk()
        self.root.title("RDT measurement")
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
        # self.tcp.disconnect()
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
        dropdown.remove(None)
        
        dropdown(
            "samples",
            root,
            values = "",
            width = 28,
            postcommand=lambda: dropdown.instances["samples"].configure(values=["a", "b", "c"]),
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
            image = TkImage("Measure", r"tools\rdt\images\Measure_Button.png").image,
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
            image = TkImage("status_bad", r"tools\rdt\images\Status_Bad.png").image
        ).place(x = 140, y = 120)
        
        self.process_display.set("GUI Built, initalizing DM")
        
    #endregion
    
    #region placeholder
    
    def measure(self):
        pass
    
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
    
    temp = rdt_app(SERVER, PORT)
    temp.startApp()

 