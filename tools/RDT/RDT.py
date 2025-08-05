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
            "Bias_on": [True, True, False]#"Bias_on": [False, True, False] #should be "Bias_on": [True, True, False]
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

        self.logger.debug(f"Initializing device {prod_name} for current and temperature measurement")
        self.Current_Tc = nidaqmx.Task()
        self.logger.debug(f"Adding AI voltage channel to {prod_name}/ai0 with min_val={self.min_val} and max_val={self.max_val}")
        self.Current_Tc.ai_channels.add_ai_voltage_chan(
            self.devices[prod_name] + "/ai0", min_val=self.min_val, max_val=self.max_val
            )
        self.logger.debug(f"Adding AI thermocouple channels to {prod_name}/ai1 and {prod_name}/ai2")
        self.Current_Tc.ai_channels.add_ai_thrmcpl_chan(
            self.devices[prod_name] + "/ai1", name_to_assign_to_channel="T_HotPlate", thermocouple_type=ThermocoupleType.K
            )
        self.logger.debug(f"Adding AI thermocouple channel to {prod_name}/ai2 for T_HotPlate2")
        self.Current_Tc.ai_channels.add_ai_thrmcpl_chan(
            self.devices[prod_name] + "/ai2", name_to_assign_to_channel="T_HotPlate2", thermocouple_type=ThermocoupleType.K
            )
        self.logger.debug("Starting Current_Tc task")
        self.Current_Tc.start()
    
    def dev2_init(self, prod_name:str):
        """
        Initializes the relay controller for the specified product.
        This method creates a nidaqmx Task and adds three digital output channels
        (line0, line1, line2) on port0 for the device associated with the given product name.
        The relay controller task is then started.
        Args:
            prod_name (str): The name of the product whose device will be initialized.
        Raises:
            KeyError: If the provided prod_name is not found in self.devices.
            nidaqmx.errors.DaqError: If there is an error initializing or starting the task.
        """
        self.logger.debug(f"Initializing relay controller for device {prod_name}")
        self.Relay_Controller = nidaqmx.Task()
        self.logger.debug(f"Adding DO channels to {prod_name}/port0/line0, {prod_name}/port0/line1, {prod_name}/port0/line2")    
        self.Relay_Controller.do_channels.add_do_chan(self.devices[prod_name] + "/port0/line0")
        self.Relay_Controller.do_channels.add_do_chan(self.devices[prod_name] + "/port0/line1")
        self.Relay_Controller.do_channels.add_do_chan(self.devices[prod_name] + "/port0/line2")
        self.logger.debug("Starting relay controller task")
        self.Relay_Controller.start()        
        
    def init_rdt(self):
        """
        Initializes the RDT system by setting up device mappings, initializing devices,
        and configuring system states.
        This method performs the following steps:
        1. Sets the initial status to False.
        2. Maps product types to device names from the local system.
        3. Attempts to initialize the first and second devices, handling exceptions and printing errors.
        4. Sets the system status to True after initialization.
        5. Writes the "Off" state to the relay controller.
        6. Reads current and temperature values from the current/temperature controller.
        7. Updates the GUI to reflect the new system state.
        Exceptions during device initialization are caught and logged, and the status is set to False.
        """
        self.Status = False
        self.logger.debug("Initializing RDT system")
        for device in self.local_system.devices:
            prod:str = str(device.product_type)
            name:str = device.name
            
            self.devices[prod] = name
        self.logger.debug(f"Device mapping: {self.devices}")
        keys:list[str] = list(self.devices.keys())
        
        self.logger.debug(f"Initializing devices: {keys[0]} and {keys[1]}")
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
        self.logger.debug("System status set to True, writing 'Off' state to relay controller")
        self.Relay_Controller.write(self.States["Off"])    
        self.logger.debug("Reading initial current and temperature values")
        self.Current_1, self.Temp_1, self.Temp_2  = self.Current_Tc.read()
        self.update_gui()
    
    def maintain_temp(self):
        """
        Controls the relay states to maintain the temperature within specified bounds.
        The method checks the current temperature (`self.Temp_1`) and sets the relay controller
        accordingly:
            - If temperature is below the lower threshold (`t_lower`), activates heating.
            - If temperature is within the acceptable range (`t_lower` < temperature < `t_upper`), maintains current state.
            - If temperature exceeds the upper threshold (`t_upper`), activates cooling.
        Relay states are set by writing a list of boolean values to `self.Relay_Controller`.
        Note:
            - `t_upper` and `t_lower` are hardcoded as 30 and 20, respectively.
            - The relay control logic may need further refinement for optimal performance.
        """
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
        """
        Updates the GUI elements with the latest readings for current and temperature.
        If an event is provided, reads the current and temperature values from the Current_Tc object.
        Formats the current and temperature values to display up to two decimal places and appends units to temperature.
        Sets the formatted values to the corresponding GUI variables.
        Triggers an update of the GUI to reflect the changes.
        Args:
            event (optional): An event object, if triggered by a GUI event. Default is None.
        """

        if event is not None:
            self.logger.debug("Event detected, reading current and temperature values")
            self.Current_1, self.Temp_1, self.Temp_2  = self.Current_Tc.read()
        
        self.logger.debug("Updating GUI with current and temperature values")
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
        # self.logger.debug(f"Current: {cur1} A, T_HotPlate: {temp1}, T_HotPlate2: {temp2}")
        # self.logger.debug("Setting GUI variables")
        self.c1.set(cur1)
        self.t1.set(temp1)
        self.t2.set(temp2)
        self.logger.debug("Updating GUI")
        self.root.update_idletasks()
        
    #end region
    #region Data Processing
    def flatten(self, data:list[list[float|str]]) -> list[float|str]:
        """
        Flattens a nested list of floats, integers, or strings into a single list.
        Args:
            data (list[list[float | str]]): A list containing sublists of floats, integers, or strings.
        Returns:
            list[float | str]: A flat list containing all elements from the nested lists.
        Example:
            >>> flatten([[1.0, 'a'], [2, 3.5], ['b']])
            [1.0, 'a', 2, 3.5, 'b']
        """


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
        """
        Executes the standard measurement procedure for the RDT tool.
        The procedure consists of:
        1. Preheating the hotplate to the bias temperature (`T_bias`) if necessary, 
           by activating the heating relay and monitoring the temperature.
        2. Activating the bias relay to begin the measurement phase.
        3. Initializing data structures and plotting axes for real-time visualization.
        4. Collecting measurements for a specified number of iterations (`N_meas`), 
           with a delay (`t_delay`) between each measurement:
            - Reads current and temperature values from the measurement device.
            - Updates the GUI and plots the data in real time.
            - Stores the measurement data in `self.data`.
        5. Saves the resulting plot to a file.
        6. Stores the collected data in instance variables for further analysis.
        Measurement data structure:
            self.data = [
                [elapsed_time, [current, T_hotplate, T_hotplate2]],
                ...
            ]
        Updates the following instance attributes:
            - self.T1: List of hotplate T1 temperatures over time.
            - self.T2: List of hotplate T2 temperatures over time.
            - self.C1: List of current measurements over time.
            - self.t:  List of time points corresponding to measurements.
        Displays progress and measurement information via print statements.
        """

        self.logger.debug("Starting standard measurement procedure")
        self.logger.debug(f"Bias temperature set to {self.T_bias} C")
        if self.Temp_1 < self.T_bias:
            self.logger.debug("Preheating hotplate to bias temperature")
            self.T_bias_flag = True
            self.logger.debug("starting heating relay")
            while self.Temp_1 < self.T_bias:
                self.Relay_Controller.write(self.States["Heat"])
                self.Current_1, self.Temp_1, self.Temp_2  = self.Current_Tc.read()
                self.update_gui()
                t.sleep(1)
        else:
            self.logger.debug("Hotplate already at or above bias temperature, skipping preheating")
            self.T_bias_flag = False
        
        self.logger.debug("Activating bias relay for measurement")
        self.Relay_Controller.write(self.States["Bias_on"])
        

        t_total:float = self.N_meas * self.t_delay

        self.logger.debug(f"Total time for measurement: {t_total} seconds")

        N:int = 0
        self.data = [] 
        #measuring code
        self.logger.debug("Initializing measurement data structures and plotting axes")
        t_start:float = t.time()
        graph_T1 = []
        graph_T2 = []
        graph_C1 = []
        graph_t = []
        for ax in self.axs:ax.clear()
        
        self.logger.debug("Setting up initial plot")
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
        self.logger.debug("Starting measurement loop")
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
        """
        Initiates and manages the cooldown process for the hotplate system.
        This method performs the following steps:
        - Initializes empty lists to store temperature, current, and time data for plotting.
        - Sets up and clears matplotlib subplots for real-time visualization.
        - Activates the cooling relay via the Relay_Controller.
        - Continuously reads current and temperature values from the Current_Tc sensor.
        - Updates the GUI and plots temperature and current data in real-time until the hotplate temperature drops below the target cooldown temperature (`self.T_cool`).
        - Deactivates the relay once cooldown is complete and closes the plot.
        The method also updates the GUI and provides console feedback during the cooldown process.
        Side Effects:
            - Updates GUI elements.
            - Plots real-time data using matplotlib.
            - Sends commands to the relay controller.
            - Prints status messages to the console.
        """
        self.logger.debug("Starting cooldown procedure")
        
        self.logger.debug(f"Target cooldown temperature: {self.T_cool} C")
        graph_T1 = []
        graph_T2 = []
        graph_C1 = []
        graph_t = []
        self.logger.debug("Setting up initial plot for cooldown")
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
        self.logger.debug("Cooldown complete, deactivating relay")
        self.Relay_Controller.write(self.States["Off"])
        
        plt.close(self.fig)
        
        # # Process the results
        # self.process_results()
        
        # # Save the data
        # self.save_data()
    #endregion

    #region shutdown
    def quit(self):
        """
        Safely shuts down the relay controller and the current test controller.

        This method performs the following actions:
        1. Turns off the relay by writing the "Off" state.
        2. Stops and closes the current test controller.
        3. Stops and closes the relay controller.

        Ensures that all hardware interfaces are properly shut down to prevent resource leaks or hardware issues.
        """
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