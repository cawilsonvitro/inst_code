#region imports
import sys, nidaqmx, time, csv
import datetime as dt
from nidaqmx.constants import (ThermocoupleType)
import nidaqmx.system
import matplotlib.pyplot as plt
import json
import traceback
import nidaqmx.task
#endregion


class NI_RDT():
    """_summary_ Class for connecting to and controlling a National Instruments device for RDT measurements.
    """
    #region init
    def __init__(self,config_path:str = "rdt_config.json"):
        #control flags
        self.T_bias_flag:bool = False
        
        # NI DEVICES
        self.devices: dict[str,str] = {}
        
        #Daq systems
        self.local_system = nidaqmx.system.System.local()
        self.Current_Tc: nidaqmx.Task  #USB9211A
        self.Relay_Controller: nidaqmx.Task  #USB6525
        
        #data buses
        self.Current_1:str 
        self.Temp_1:str
        self.Temp_2:str
        
        
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


        try:
            self.dev2_init(keys[1])
        except Exception as e:  
            print(f"Error initializing device {keys[1]}: {e}")
            traceback.print_exc()
            
        #initalizing system
        
        self.Relay_Controller.write(self.States["Off"])    
        
        temp: list[str]
        temp = self.Current_Tc.read()
        print(temp)
        
        # self.Current_1, self.Temp_1, self.Temp_2 
        
        
        
        # if self.Temp_1 > self.T_bias:self.T_bias_flag = True
        # else:self.T_bias_flag = False
        
    #endregion
    #region measurement
    def standard_procedure(self):
        """_summary_ Standard procedure for RDT measurements.
        """
        # Initialize the RDT device
        self.init_rdt()
        
        # # Perform the measurement
        # self.perform_measurement()
        
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
    rdt = NI_RDT()
    try:
        rdt.load_config()
        rdt.init_rdt()
        rdt.quit()
    except:
        traceback.print_exc()
        print("ERROR")
        rdt.Current_Tc.stop()
        rdt.Current_Tc.close()
        rdt.Relay_Controller.stop()
        rdt.Relay_Controller.close()