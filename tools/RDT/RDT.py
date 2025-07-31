#region imports
import nidaqmx
from datetime import datetime as dt
from nidaqmx.constants import (ThermocoupleType)
import nidaqmx.system
import matplotlib.pyplot as plt
import json
import traceback
import time as t
import logging
from logging.handlers import TimedRotatingFileHandler
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

class NI_RDT():
    """_summary_ Class for connecting to and controlling a National Instruments device for RDT measurements.
    """
    #region init
    def __init__(self, root, c1, t1, t2, config_path:str = r"C:\Users\c376038\Desktop\inst_suite\working\tools\RDT\rdt_config.json"):
        #control flags
        self.T_bias_flag:bool = False
        
        # NI DEVICES
        self.devices: dict[str,str] = {}
        
        #Daq systems
        self.local_system = nidaqmx.system.System.local()
        self.R: nidaqmx.Task  #USB9211A
        self.Relay_Controller: nidaqmx.Task  #USB6525
        
        #front end interface
        self.root = root
        self.c1 = c1
        self.t1 = t1
        self.t2 = t2
        
        
        #data buses
        self.Current_1:str 
        self.Temp_1:str
        self.Temp_2:str
        self.data:list[list[float|str|int]] = [] 
        
        #stuff to pull from config 
        # self.t_run:float = 0.0
        self.t_delay:float = 1.0
        self.T_cool:int = 130
        self.N_meas:int = 0
        
        #config 
        self.config_path:str  = config_path
        self.config:dict[str,dict[str,str]]
        self.sys_config:dict[str,str]
        
        #states
        self.States: dict[str,list[bool]] = {
            "Off": [False, False, False],
            "Heat": [True, False, False],
            "Cool": [False, False, True],
            "Bias_on": [True, True, False]
        }
        self.Status = False
        
        #graphing
        self.fig, self.axs, = plt.subplots(2,1)
        self.fig.set_size_inches(8,6)
        
    def load_config(self): #this will need to be replaced with front end config loading
        """_summary_ Load the configuration from the JSON file.
        """
        try:
            with open(self.config_path, 'r') as file:
                self.config:dict[str,dict[str,str]] = json.load(file)
            print(list(self.config.keys()))
            self.sys_config = self.config['RDT']['sys']
            print(self.sys_config)
            self.T_bias:float = float(self.sys_config["T_Bias_on"])
            

        except FileNotFoundError:
            print(f"Configuration file {self.config_path} not found.")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from the configuration file {self.config_path}.")
        
    def dev1_init(self, prod_name:str):
        """
        wrapper for usb init
        """
        
        min_val:float = float(self.config["RDT"][prod_name]["Min_val"])
        
        max_val:float = float(self.config["RDT"][prod_name]["Max_val"])
        
        self.Current_Tc = nidaqmx.Task()
        
        self.Current_Tc.ai_channels.add_ai_voltage_chan(
            self.devices[prod_name] + "/ai0", min_val=min_val, max_val=max_val
            )
        self.Current_Tc.ai_channels.add_ai_thrmcpl_chan(
            self.devices[prod_name] + "/ai1", name_to_assign_to_channel="T_HotPlate", thermocouple_type=ThermocoupleType.K
            )
        self.Current_Tc.ai_channels.add_ai_thrmcpl_chan(
            self.devices[prod_name] + "/ai2", name_to_assign_to_channel="T_HotPlate2", thermocouple_type=ThermocoupleType.K
            )
        
        self.Current_Tc.start()
    
    def dev2_init(self, prod_name:str):
        """wrapper for usb init"""
        self.Relay_Controller = nidaqmx.Task()
        self.Relay_Controller.do_channels.add_do_chan(self.devices[prod_name] + "/port0/line0")
        self.Relay_Controller.do_channels.add_do_chan(self.devices[prod_name] + "/port0/line1")
        self.Relay_Controller.do_channels.add_do_chan(self.devices[prod_name] + "/port0/line2")
        self.Relay_Controller.start()        
        
    def init_rdt(self):
        self.Status = False
        for device in self.local_system.devices:
            prod:str = str(device.product_type)
            name:str = device.name
            
            self.devices[prod] = name
            
        keys:list[str] = list(self.devices.keys())
        
        try:
            self.dev1_init(keys[0])
        except Exception as e:
            print(f"Error initializing device {keys[0]}: {e}")
            traceback.print_exc()
            self.Status = False
        

        try:
            self.dev2_init(keys[1])
        except Exception as e:  
            print(f"Error initializing device {keys[1]}: {e}")
            traceback.print_exc()
            self.Status = False
            
        #initalizing system
        self.Status = True
        self.Relay_Controller.write(self.States["Off"])    
        self.Current_1, self.Temp_1, self.Temp_2  = self.Current_Tc.read()
        self.update_gui()
    #endregion
    #region front end interface
    def update_gui(self, event = None):
        """_summary_ Update the GUI with the current values.
        """
        # print(f"Current: {self.Current_1} A, T_HotPlate: {self.Temp_1} C, T_HotPlate2: {self.Temp_2} C")
        if event is not None:
            self.Current_1, self.Temp_1, self.Temp_2  = self.Current_Tc.read()
            
        cur1 = str(self.Current_1)
        print(cur1)
        cur1e = cur1[cur1.index("e"):] if "e" in cur1 else ""
        cur1 = cur1[:cur1.index(".") + 3] if "." in cur1 else cur1
        if cur1e != "":cur1 = f"{cur1}{cur1e}"
        temp1 = str(self.Temp_1)
        temp1 = temp1[:temp1.index(".") + 3] if "." in temp1 else temp1
        temp2 = str(self.Temp_2)
        temp2 = temp2[:temp2.index(".") + 3] if "." in temp2 else temp2
        temp1 += " C"
        temp2 += " C"   
        self.c1.set(cur1)
        self.t1.set(temp1)
        self.t2.set(temp2)
        print()
        self.root.update_idletasks()
        
    #end region
    #region Data Processing
    def flatten(self, data:list[list[float|str]]) -> list[float]:
        """_summary_ Flatten a 2D list into a 1D list."""
        flat:list[float|str] = []
        for object in data:
            if isinstance(object, list):
                for item in object:
                    if isinstance(item, (float, int, str)):
                        flat.append(item)
            else:
                if isinstance(object, (float, int, str)):
                    flat.append(object)
        return flat
        
    #endregion
    #region measurement func
    
    
    
    #endregion
    #region measurement
    def standard_procedure(self):
        """_summary_ Standard procedure for RDT measurements.
        """


        if self.Temp_1 < self.T_bias:
            self.T_bias_flag = True
            while self.Temp_1 < self.T_bias:
                self.Relay_Controller.write(self.States["Heat"])
                self.Current_1, self.Temp_1, self.Temp_2  = self.Current_Tc.read()
                self.update_gui()
                # print(f"Current: {self.Current_1} A, T_HotPlate: {self.Temp_1} C, T_HotPlate2: {self.Temp_2} C")        
                t.sleep(1)
        else:
            print("PreHeated")
            self.T_bias_flag = False
        
        self.Relay_Controller.write(self.States["Bias_on"])
        
        self.N_meas:int = 1
        
        t_total:float = self.N_meas * self.t_delay 
        
        print(f"Total time for measurement: {t_total} seconds")
        
        N:int = 0
        self.data = [] 
        #measuring code
        
        t_start:float = t.time()
        graph_T1 = []
        graph_T2 = []
        graph_C1 = []
        graph_t = []
        for ax in self.axs:ax.clear()
        
        self.axs[0].plot(graph_t, graph_T1, c = 'b', label = 'Hotplate T1')
        self.axs[0].plot(graph_t, graph_T1, c = 'r', label = 'Hotplate T2')
        self.axs[0].legend()
        self.axs[1].plot(graph_t, graph_C1, c = 'y', label = 'Current')
        self.axs[1].legend()
        
        self.axs[0].set_title("Temperature vs Time")
        self.axs[0].set_xlabel("Time (s)")
        self.axs[0].set_ylabel("Temperature (C)")
        self.axs[1].set_title("Current vs Time")
        self.axs[1].set_xlabel("Time (s)")
        self.axs[1].set_ylabel("Current (A)")
        self.fig.show()
        
        while N <= self.N_meas:
            temp:list[float|str] = []
            temp.append(t_start - t.time())
            self.Current_1, self.Temp_1, self.Temp_2  = self.Current_Tc.read()
            
            graph_T1.append(self.Temp_1)
            graph_T2.append(self.Temp_2)
            graph_C1.append(self.Current_1)
            graph_t.append(N)
            self.update_gui()
            
            temp.append([self.Current_1, self.Temp_1, self.Temp_2])
            self.data.append(temp)
            
            self.axs[0].plot(graph_t, graph_T1, c = 'b', label = 'Hotplate T1')
            self.axs[0].plot(graph_t, graph_T2, c = 'r', label = 'Hotplate T2')

            self.axs[1].plot(graph_t, graph_C1, c = 'y', label = 'Current')
            
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

            # plt.pause(0.005)  # Allow the plot to update
             #struct of data
             # data = [[time, [current, T_hotplate, T_hotplate2]], ...]
            print(f"Time: {t_start - t.time()},Current: {self.Current_1} A, T_HotPlate: {self.Temp_1} C, T_HotPlate2: {self.Temp_2} C")
            print(N)
            N +=1
            t.sleep(self.t_delay)
        self.fig.savefig(f'tools\\RDT\\graphs\\{date}.png')


        self.T1 = graph_T1
        self.T2 = graph_T2
        self.C1 = graph_C1
        self.t = graph_t
        
        

    def cooldown(self):
        graph_T1 = []
        graph_T2 = []
        graph_C1 = []
        graph_t = []
        plt.close(self.fig)
        self.fig, self.axs = plt.subplots(2,1)
        for ax in self.axs:ax.clear()
        self.axs[0].plot(graph_t, graph_T1, c = 'b', label = 'Hotplate T1')
        self.axs[0].plot(graph_t, graph_T1, c = 'r', label = 'Hotplate T2')
        self.axs[0].legend()
        self.axs[1].plot(graph_t, graph_C1, c = 'y', label = 'Current')
        self.axs[1].legend()
        
        self.axs[0].set_title("Temperature vs Time")
        self.axs[0].set_xlabel("Time (s)")
        self.axs[0].set_ylabel("Temperature (C)")
        self.axs[1].set_title("Current vs Time")
        self.axs[1].set_xlabel("Time (s)")
        self.axs[1].set_ylabel("Current (A)")
        self.fig.show()
        self.Relay_Controller.write(self.States["Cool"])
        
        print("Cooling down...")
        
        self.fig.suptitle("Cooling Down")
        N = 0
        currenttemp = self.Current_Tc.read()[1]
        while self.T_cool < currenttemp:
            self.Current_1, self.Temp_1, self.Temp_2  = self.Current_Tc.read()
            self.update_gui()
            # print(f"Current: {self.Current_1} A, T_HotPlate: {self.Temp_1} C, T_HotPlate2: {self.Temp_2} C")
            currenttemp = self.Temp_1
            graph_T1.append(self.Temp_1)
            graph_T2.append(self.Temp_2)
            graph_C1.append(self.Current_1)
            graph_t.append(N)
            self.axs[0].plot(graph_t, graph_T1, c = 'b', label = 'Hotplate T1')
            self.axs[0].plot(graph_t, graph_T2, c = 'r', label = 'Hotplate T2')

            self.axs[1].plot(graph_t, graph_C1, c = 'y', label = 'Current')
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            
            N += 1
            t.sleep(1)
        self.Relay_Controller.write(self.States["Off"])
        
        plt.close(self.fig)
        
        # # Process the results
        # self.process_results()
        
        # # Save the data
        # self.save_data()
    #endregion

    #region shutdown
    def quit(self):
        self.Relay_Controller.write(self.States["Off"])
        self.Current_Tc.stop()
        self.Current_Tc.close()
        self.Relay_Controller.stop()
        self.Relay_Controller.close()   
        
    #endregion
if __name__ == "__main__":
    rdt:NI_RDT = NI_RDT("", "", "", "")
    try:
        rdt.load_config()
        rdt.init_rdt()
        print(rdt.T_cool)
        rdt.Relay_Controller.write(rdt.States["Bias_on"])
        t.sleep(5)
        
        rdt.Relay_Controller.write(rdt.States["Off"])
        # rdt.cooldown()
        # rdt.Relay_Controller.write(rdt.States["Cool"])
        # while 0 < rdt.Current_Tc.read()[1]:
        #     rdt.Current_1, rdt.Temp_1, rdt.Temp_2  = rdt.Current_Tc.read()
        #     print(f"Current: {rdt.Current_1} A, T_HotPlate: {rdt.Temp_1} C, T_HotPlate2: {rdt.Temp_2} C")
        #     t.sleep(1)
        # rdt.Relay_Controller.write(rdt.States["Off"])
        # # rdt.standard_procedure()
        # # rdt.quit()
        # # print(rdt.data)
    except:
        traceback.print_exc()
        print("ERROR")
        try:
            rdt.quit()
        except:
            rdt.Current_Tc.stop()
            rdt.Current_Tc.close()
            rdt.Relay_Controller.stop()
            rdt.Relay_Controller.close()