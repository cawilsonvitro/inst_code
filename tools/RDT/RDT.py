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
    """
    NI_RDT is a class for controlling and automating measurements using National Instruments DAQ devices,
    specifically for Resistive Device Testing (RDT) setups. It manages device initialization, measurement
    procedures, data acquisition, GUI updates, and cooldown routines.
    Attributes:
        T_bias_flag (bool): Flag indicating if bias temperature is reached.
        devices (dict[str, str]): Mapping of device product types to device names.
        local_system (nidaqmx.system.System): Local NI DAQ system.
        R (nidaqmx.Task): Task for USB9211A device (not directly used in code).
        Relay_Controller (nidaqmx.Task): Task for controlling relays (USB6525).
        root: GUI root object.
        c1, t1, t2: GUI elements for displaying current and temperature readings.
        Current_1 (str): Current measurement value.
        Temp_1 (str): First temperature measurement value.
        Temp_2 (str): Second temperature measurement value.
        data (list[list[float|str|int]]): List of measurement data.
        t_delay (float): Delay between measurements.
        T_cool (int): Target temperature for cooldown.
        N_meas (int): Number of measurements to perform.
        T_bias (float): Bias temperature threshold.
        min_val (float): Minimum value for voltage channel.
        max_val (float): Maximum value for voltage channel.
        States (dict[str, list[bool]]): Relay states for different modes.
        Status (bool): Status flag for system initialization.
        fig, axs: Matplotlib figure and axes for plotting.
        T1, T2, C1, t: Lists for storing graph data.
    Methods:
        __init__(...): Initializes the NI_RDT instance and its configuration.
        dev1_init(prod_name): Initializes the analog input channels for current and temperature.
        dev2_init(prod_name): Initializes the digital output channels for relay control.
        init_rdt(): Initializes the RDT system and devices.
        update_gui(event=None): Updates the GUI with the latest measurement values.
        flatten(data): Flattens a 2D list into a 1D list.
        standard_procedure(): Executes the standard measurement procedure, including heating, biasing, and data collection.
        cooldown(): Executes the cooldown procedure, monitoring temperature until target is reached.
        quit(): Safely shuts down and releases all DAQ tasks and resources.
    """
    #region init
    def __init__(self, root, c1, t1, t2, T_bias_on, t_run, t_delay,fan_delay, T_cool, num_of_meas, min_val, max_val):
        """
        Initializes the RDT class with configuration parameters, hardware interfaces, and state management.
        Args:
            root: The root GUI element or main window.
            c1: Front-end interface parameter (usage context-specific).
            t1: Front-end interface parameter (usage context-specific).
            t2: Front-end interface parameter (usage context-specific).
            T_bias_on (float): Bias temperature value to be set when bias is on.
            t_run: (Unused in this method; possibly for future use).
            t_delay (float): Delay time before starting measurements.
            fan_delay: (Unused in this method; possibly for future use).
            T_cool (int): Cooling temperature threshold.
            num_of_meas (int): Number of measurements to perform.
            min_val (float): Minimum value for measurement or validation.
            max_val (float): Maximum value for measurement or validation.
        Attributes:
            T_bias_flag (bool): Control flag for bias temperature.
            devices (dict[str, str]): Dictionary of NI device names and identifiers.
            local_system: NI DAQmx local system object.
            R: NI DAQmx Task for USB9211A.
            Relay_Controller: NI DAQmx Task for USB6525.
            Current_1 (str): Data bus for current measurement.
            Temp_1 (str): Data bus for first temperature measurement.
            Temp_2 (str): Data bus for second temperature measurement.
            data (list[list[float|str|int]]): Collected measurement data.
            t_delay (float): Delay before measurement.
            T_cool (int): Cooling temperature threshold.
            N_meas (int): Number of measurements.
            T_bias (float): Bias temperature value.
            min_val (float): Minimum measurement value.
            max_val (float): Maximum measurement value.
            States (dict[str, list[bool]]): Dictionary of system states.
            Status (bool): Current status of the system.
            fig, axs: Matplotlib figure and axes for graphing.
        """
        
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
        self.t_delay:float = t_delay
        self.T_cool:int = T_cool
        self.N_meas:int = num_of_meas
        self.T_bias:float = T_bias_on
        self.min_val:float = min_val
        self.max_val:float = max_val
        
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
        #logging
        class_name = str(type(self))
        name = class_name.split(" ")[-1][:-1].replace("'", "")
        self.logger = logging.getLogger(name)
        logging.debug("rdt class initialized")
        
    def dev1_init(self, prod_name:str):
        """
        Initializes the NI-DAQmx task for the specified device, configuring voltage and thermocouple channels.
        Args:
            prod_name (str): The product name or device identifier used to select the appropriate NI-DAQmx device.
        Side Effects:
            - Creates and assigns a nidaqmx.Task to self.Current_Tc.
            - Adds an analog voltage channel (ai0) with specified min and max values.
            - Adds two thermocouple channels (ai1 and ai2) of type K, named "T_HotPlate" and "T_HotPlate2".
            - Starts the NI-DAQmx task for data acquisition.
        """

        self.Current_Tc = nidaqmx.Task()
        
        self.Current_Tc.ai_channels.add_ai_voltage_chan(
            self.devices[prod_name] + "/ai0", min_val=self.min_val, max_val=self.max_val
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
    
    def maintain_temp(self):
        #need to make better 
        t_upper = 30
        t_lower = 20 
        if self.Temp_1 < t_lower:
            self.Relay_Controller.write([True, True, False])
        
        if t_lower < self.Temp_1 < t_upper and self.Temp_1 < t_upper:
            self.Relay_Controller.write([False, True, False])
        
        if self.Temp_1 > t_upper:
            self.Relay_Controller.write([False, True, True])     
        
    #endregion
    #region front end interface
    def update_gui(self, event = None):
        """_summary_ Update the GUI with the current values.
        """
        # print(f"Current: {self.Current_1} A, T_HotPlate: {self.Temp_1} C, T_HotPlate2: {self.Temp_2} C")
        if event is not None:
            self.Current_1, self.Temp_1, self.Temp_2  = self.Current_Tc.read()
            
        cur1 = str(self.Current_1)
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
        test = [True] * 3
        rdt.Relay_Controller.write(rdt.States["Bias_on"])
        i = 0
        current = []
        while i < 10:
            rdt.Current_1, rdt.Temp_1, rdt.Temp_2  = rdt.Current_Tc.read()
            current.append(rdt.Current_1)
            print(f"Current: {rdt.Current_1} A, T_HotPlate: {rdt.Temp_1} C, T_HotPlate2: {rdt.Temp_2} C")
            i += 1
            t.sleep(1)
        rdt.Current_Tc.stop()
        rdt.Current_Tc.close()
        rdt.Relay_Controller.stop()
        rdt.Relay_Controller.close()
        plt.plot(current)
        # rdt.Relay_Controller.write(rdt.States["Off"])
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