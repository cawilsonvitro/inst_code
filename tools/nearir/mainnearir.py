#region imports
from gui_package_cawilvitro import *
from instutil import inst_util as iu
# import nearir as IR
import nearir_dummy as IR
import sys
from datetime import datetime as dt
import traceback
import logging
from logging.handlers import TimedRotatingFileHandler
from functools import partial
#endregion

#region logging

date = dt.now().strftime("%m-%d-%Y, Hour %H Min %M Sec %S")

logging.basicConfig(
    level=logging.DEBUG, # Set a global logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.StreamHandler(), # Log to console
        TimedRotatingFileHandler(f'tools\\nearir\\logs\\{date}.log', when = "D", backupCount= 5)
    ]
)


#endregion

class near_ir_app():
    """
    near_ir_app(ip, port)
    A GUI application for Near-Infrared (NIR) measurement, providing TCP client-server communication, spectrometer control, and data management.
    Attributes:
        quit (bool): Flag to indicate application shutdown.
        process_display (tk.StringVar): Displays the current process state in the GUI.
        samples (list): List of sample identifiers.
        spectrometer: Instance of the spectrometer driver.
        value: Measurement value.
        dataPath (str): Path to store measurement data.
        sample_num (int): Current sample number.
        exst (str): File extension for data files.
        fmanager (iu.FileManager): File manager for data operations.
        description (str): Description of the current sample.
        logger (logging.Logger): Logger for application events.
        ip (str): Server IP address.
        port (int): Server port.
        connected (bool): TCP connection status.
        tcp: TCP client instance.
        root (tk.Tk): Main Tkinter window.
        wait (tk.BooleanVar): Variable to synchronize GUI events.
        desc_window (tk.Toplevel): Window for editing sample descriptions.
        position (str): Selected sample position.
        wvs (str): Comma-separated wavelengths.
        spec (str): Comma-separated spectral data.
    Methods:
        __init__(ip, port):
            Initializes the application, sets up logging, and prepares attributes.
        connectClient():
            Establishes a TCP connection to the server, updates connection status, and handles UI feedback.
        startApp():
            Initializes and starts the main GUI application loop.
        endApp(event):
            Handles application shutdown, disconnects from server, and cleans up resources.
        toggle_desc():
            Toggles the visibility of the sample description window.
        get_desc(event):
            Retrieves and processes the sample description from the description window.
        get_pos(event):
            Retrieves the selected sample position from the GUI.
        update():
            Updates the sample dropdown menu with values from the server.
        buildGUI(root):
            Constructs and initializes all GUI components and windows.
        init_spec():
            Initializes the spectrometer driver and updates the UI with driver status.
        tcp_proptocol():
            Handles the TCP communication protocol for sample measurement and metadata exchange.
        measure():
            Performs a measurement, processes results, manages data storage, and communicates with the server.
    """
    #region application start up
    def __init__(self, ip, port):
        '''
        init class for use
        '''
        self.quit = False
        
        self.process_display = None
        self.samples = []
        
        #spectrometer
        self.spectrometer = None

        #data management
        self.value = None
        self.dataPath = r"data/"
        self.sample_num:int
        self.exst = ".csv"
        self.fmanager:iu.FileManager = iu.FileManager("nearir", "5")
        self.description: str = "None"
        #threading
        # self.message: Queue[Any] = Queue(maxsize=1)
        # self.response: Queue[Any] = Queue(maxsize=1)
        
        #logging

        class_name = str(type(self))
        name = class_name.split(" ")[-1][:-1].replace("'", "")
        
        self.logger = logging.getLogger(name)
        
        self.logger.info("4 point probe app initalized")
        
        #tcp 
        self.ip, self.port = (ip, port)  
        

    
    def connectClient(self) -> None:
        """
        Attempts to establish a TCP connection to the server using the specified IP and port.
        Updates the connection status and logs relevant information or errors.
        On successful connection, updates the UI to indicate a good connection and sends an ID to the server.
        On failure, updates the UI to indicate a bad connection and logs the error.
        Side Effects:
            - Updates self.connected to reflect connection status.
            - Logs connection attempts, successes, and failures.
            - Updates the "Connection" status label in the UI.
            - Sends an ID to the server upon successful connection.
        Exceptions:
            - Handles and logs exceptions that occur during connection or ID sending.
        """
        self.logger.info(f"Connecting to server {self.ip}:{self.port}")
        self.connected:bool = False
        
        
        try:            
            self.tcp = iu.client(self.ip, self.port)#, self.message, self.response)
            result = self.tcp.connect()
            if result != None:
                self.connected = False
                self.logger.error(traceback.format_exc())
            else:
                self.logger.info("Connect to server")
                self.connected = True
        except Exception as e:
            traceback.print_exc()
            self.connected = False
            
        if self.connected:
            self.logger.info(f"Connected to server {self.ip}:{self.port}")
            StandardLabel.instances["Connection"].configure(image = TkImage("connection_status", r"images\Status_Good.png").image)
            try:
                self.tcp.id()
            except Exception as e:
                self.logger.error(f"Failed to send id to server")
        else:
            StandardLabel.instances["Connection"].configure(image = TkImage("connection_status", r"images\Status_Bad.png").image)
            self.logger.error(f"Failed to connect to server, see above for details")
    
    def startApp(self):
        """
        Initializes and starts the NIR (Near-Infrared) measurement application GUI.

        This method performs the following actions:
            - Logs the start of the application.
            - Creates the main Tkinter window with a fixed size and title.
            - Sets up window event bindings for Escape key and window close.
            - Initializes a StringVar to display the current process state.
            - Builds the GUI components.
            - Establishes a client connection.
            - Starts the Tkinter main event loop.

        Returns:
            None
        """
        self.logger.info("Starting NIR app")
        self.root = tk.Tk()
        self.root.title("NIR measurement")
        self.root.geometry("480x240")
        self.root.resizable(width=False,height=False)
        self.root.bind("<Escape>", self.endApp)
        self.root.protocol("WM_DELETE_WINDOW",partial(self.endApp, None))
        self.process_display = tk.StringVar() 
        self.process_display.set("Booting")
        self.root.update_idletasks()
        self.buildGUI(self.root)
        self.connectClient()
        self.logger.info("GUI built, starting main loop")
        self.root.mainloop()
    
    #endregion
    
    #region app control  
    
    def endApp(self, event):
        """
        Handles the shutdown process for the application.

        This method performs the following actions:
        - Logs the shutdown event.
        - Sets the quit flag to True to indicate the application should terminate.
        - Attempts to disconnect from the TCP client if connected.
        - Handles any exceptions if the client is already shut down.
        - Shuts down the spectrometer if it is active.
        - Quits the main application loop.

        Args:
            event: The event object triggering the shutdown (typically from a GUI event).
        """
        '''
        ends application
        '''
        self.logger.info("Shutting down application")
        self.quit = True
        try:
            if self.connected: 
                self.tcp.disconnect()
        except:
            self.logger.debug("client already shut down")
        if self.spectrometer is not None:
            self.spectrometer.quit()
        self.root.quit()
        
        
    #endregion
   
    #region  GUI
        
    def toggle_desc(self):
        """
        Toggles the visibility of the description window.

        If the description window is currently visible ("normal" state), it will be hidden.
        If the description window is currently hidden ("withdrawn" state), it will be shown.
        Logs the toggle action for debugging purposes.
        """
        self.logger.info("Toggling Description Window")
        state = self.desc_window.state()
        if state == "normal": self.desc_window.withdraw()
        if state == "withdrawn": self.desc_window.deiconify()

    
    def get_desc(self, event) ->None:
        """
        Handles the event to retrieve and process the description text from the 'desc' TextBox.
        This method performs the following actions:
            - Retrieves the current text from the 'desc' TextBox instance and stores it in self.description.
            - Clears the text from the 'desc' TextBox.
            - Toggles the description UI element (e.g., hides or shows it).
            - Signals that the waiting state is over by setting self.wait to False.
        Args:
            event: The event object that triggered this method (typically from a GUI event binding).
        Returns:
            None
        """
        #closes out window and gets info
        self.description = TextBox.instances["desc"].get("1.0","end-1c")
        TextBox.instances["desc"].delete("1.0","end-1c")
        self.toggle_desc()
        
        self.wait.set(False)

    def get_pos(self,event) -> None: 
        """
        Retrieves the currently selected position from the 'position' dropdown and updates the instance's position attribute.
        Args:
            event: The event object associated with the dropdown selection.
        Side Effects:
            - Updates self.position with the selected value from dropdown.instances["position"].
            - Logs debug messages before and after retrieving the position.
        """
               
        self.logger.debug("Getting pos")
        self.position = "" 
        self.position = dropdown.instances["position"].get()
        self.logger.debug(f"{self.position} selected")
    
    
    
    
    def update(self) -> None:
        """
        Updates the "samples" dropdown menu with values received from the TCP server.
        This method sends an "UPDATE" command to the server via the TCP socket, receives a response,
        and updates the dropdown menu labeled "samples" with the new values. If the server response
        is "None", the dropdown is cleared. The update action is logged, and the server response is
        printed for debugging purposes.
        """
        self.logger.info("Updating sample dropdown")
        self.tcp.soc.send("UPDATE".encode())
        resp:str = self.tcp.soc.recv(1024).decode()
        print(resp)
        if resp != "None":
            dropdown.instances["samples"].configure(values=resp.split(","))
        else:
            dropdown.instances["samples"].configure(values=[])
        
    def toggle_id(self):
        self.logger.info("Toggling ID Window")
        state = self.id_window.state()
        if state == "normal":self.id_window.withdraw()
        if state == "withdrawn":self.id_window.deiconify()
        
    def get_id(self, event) -> None:
        self.logger.debug("Getting ID")
        self.id = TextBox.instances["id"].get("1.0","end-1c")
        print(self.id)
        TextBox.instances["id"].delete("1.0","end-1c")
        self.toggle_id()
        
        self.wait.set(False)
        
    def buildGUI(self, root):
        """
        Constructs and initializes the graphical user interface (GUI) for user interaction.
        This method sets up all necessary widgets, including dropdowns, labels, buttons, and status indicators,
        and arranges them within the main application window. It also creates a separate description window for
        sample descriptions, configures widget callbacks, and initializes relevant variables for GUI state tracking.
        Args:
            root (tk.Tk or tk.Frame): The root window or frame to which the GUI components will be attached.
        Side Effects:
            - Modifies the GUI by adding and placing widgets.
            - Initializes and configures instance variables related to GUI state.
            - Logs the GUI building process.
            - Calls self.init_spec() to initialize the driver after GUI setup.
        """
        self.logger.info("Building GUI")
        Button.remove(None)
        Label.remove(None)
        StandardLabel.remove(None)
        dropdown.remove(None)
        
        
        #to track our var
        self.wait:tk.BooleanVar = tk.BooleanVar()
        
        self.wait.set(False)
        
        #main window
        
        dropdown(
            "samples",
            root,
            values = "",
            width = 28,
            postcommand= self.update,
        ).place(x = 0, y = 60)
        dropdown(
            "position",
            root,
            values = ["LT", "LC", "LL", "CT", "CC", "CL", "RT", "RC", "RL"],
            width = 5,
        ).place(x = 200, y = 60)
        dropdown.instances["position"].bind('<<ComboboxSelected>>', self.get_pos)
        Label(
            "positions",
            root,
            text = "position:",
            anchor=tk.W,           
            height=1,              
            width=30,              
            bd=1,                  
            font=("Arial", 10), 
            cursor="hand2",   
            fg="black",                           
            justify = tk.LEFT,  
            wraplength=100   
            ).place(x = 200, y = 40, width = 80,height = 20)
        
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
        
        StandardButtons(
            "Reconnect",
            root,
            image = TkImage("Reconnect", r"tools\nearir\images\Reconnect_Button.png").image,
            command = self.connectClient
        ).place(x = 0, y = 190)
        
        StandardLabel(
            "Connection",
            root,
            image = TkImage("Connect_status",  r"tools\nearir\images\Status_Bad.png").image
        ).place(x = 140, y = 190)
        
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
        
        #description window
        TextBox.remove(None) #here so we only have to call this once might havet to switch
        self.desc_window = tk.Toplevel(self.root)
        self.desc_window.geometry("300x800")
        self.desc_window.title("Sample Description")
        self.desc_window.bind('<Escape>', self.get_desc)
        self.desc_window.protocol("WM_DELETE_WINDOW", partial(self.get_desc, None))
        TextBox("desc", self.desc_window, height = 20, width = 32).place(x = 10, y = 50)
        self.desc_window.withdraw()
        
        self.process_display.set("GUI Built, initalizing Driver")
        self.logger.info("GUI built, initializing Driver")
        self.init_spec()

        #operator id window
        self.id_window = tk.Toplevel(self.root)
        self.id_window.geometry("300x300")
        self.id_window.title("Operator ID")
        self.id_window.bind('<Escape>', self.get_id)
        self.id_window.protocol("WM_DELETE_WINDOW", partial(self.get_id, None))
        TextBox("id", self.id_window, height = 2, width = 30).place(x = 10, y = 50)
        Label(
            "Operator_ID",
            self.id_window,
            text = "Operator ID:",
            anchor=tk.W,           
            height=1,              
            width=30,              
            bd=1,                  
            font=("Arial", 10), 
            cursor="hand2",   
            fg="black",                           
            justify = tk.LEFT,  
            wraplength=100   
            ).place(x = 0, y = 30, width = 80,height = 20)
        self.id_window.withdraw()
        
    #endregion
    
    #region spectrometer
    def init_spec(self):
        """
        Initializes the spectrometer driver and updates the UI with the driver status.
        This method attempts to load and initialize the spectrometer driver using the IRstellarnet class.
        It updates the process display and root UI to indicate loading status. If the driver loads successfully,
        it displays a "Status Good" image and logs a success message. If the driver fails to load, it displays
        a "Status Bad" image and logs an error message. Any exceptions during initialization are printed to the console.
        Side Effects:
            - Updates the process display and root UI.
            - Sets self.spectrometer with the initialized driver.
            - Logs status messages.
            - Displays status images on the UI.
        """
        self.logger.info("Loading driver")
        self.process_display.set("Loading Driver")
        self.root.update_idletasks()
        try:
            self.spectrometer = IR.stellarnet(connection_string="123",int_time=1000, scans_to_avg=1, x_smooth=0, x_timing=3)
            self.spectrometer.init_driver()
            
        except Exception as e:
            traceback.print_exc()
            
        if self.spectrometer.status:
            StandardLabel(
                "Status",
                self.root,
                image = TkImage("status_Bad",r"tools\nearir\images\Status_Good.png").image,
            ).place(x = 140, y = 120)
            self.logger.info("Driver loaded successfully")
        else:
            StandardLabel(
                "Status",
                self.root,
                image = TkImage("status_bad", r"tools\nearir\images\Status_Bad.png").image
            ).place(x = 140, y = 120)
            self.logger.error("Failed to load driver, see above for details")
        self.process_display.set("Drivers loaded, Ready")
    
    #endregion
    
    #region data management
    def tcp_proptocol(self) -> None:
        """
        Handles the TCP protocol communication sequence with the server for sample measurement.
        This method performs the following steps:
        1. Sends a "META" command to the server and processes the response.
        2. Sends the sample number and receives a response.
        3. Sends the sample position (or "None" if not specified) and receives a description from the server.
        4. Displays the received description in the UI and waits for user input or confirmation.
        5. Initiates the "MEAS" protocol by sending the "MEAS" command and follows up with sample ID, description, and value.
        6. Checks for the expected server response and logs errors if the response is unexpected.
        7. Sends the sample spectra to the server and processes the final response.
        All communication steps and responses are logged for debugging and traceability.
        """
        self.logger.info("Starting TCP protocol")
        
        self.logger.debug("Sending META command to server")
        
        self.tcp.soc.send("META".encode())
        resp = self.tcp.soc.recv(1024).decode()
        
        self.logger.debug(f"Received response: {resp}")
        self.logger.debug("Sending sample number to server")
        
        self.tcp.soc.send(str(self.sample_num).encode())
        resp = self.tcp.soc.recv(1024).decode()
        
        self.logger.debug(f"Received response: {resp}")
        self.logger.debug("Sending position to server")
        if self.position == "": self.position = "None"
        
        self.tcp.soc.send(self.position.encode())
        self.description = self.tcp.soc.recv(1024).decode()
        
        self.logger.debug(f"got {self.description} from server")
        self.logger.debug("Sending description request to server")

        TextBox.instances["desc"].insert("1.0", self.description)
        self.logger.debug(f"Server sent sample description {self.description}, launched description editor")
        self.process_display.set("Please enter sample, if no description needed enter none")
        self.wait.set(True)
        self.toggle_id()
        self.root.wait_variable(self.wait)
            
        self.wait.set(True)
        self.toggle_desc()
        self.root.wait_variable(self.wait)
        self.logger.debug(f"user set description to {self.description}")

        self.logger.info("Starting TCP MEAS protocol")
        self.logger.debug("Sending MEAS command")
        
        self.tcp.soc.send("MEAS".encode())
        
        resp = self.tcp.soc.recv(1024).decode()
        self.logger.debug(f"got {resp} from Server")
        self.logger.debug(f"sending sample id {self.sample_num}")
        
        self.tcp.soc.send(self.sample_num.encode())
        resp = self.tcp.soc.recv(1024).decode()
        
        self.logger.debug(f"Received response: {resp}")
        
        self.tcp.soc.send(self.description.encode())
        resp = self.tcp.soc.recv(1024).decode()
        
        self.logger.debug(f"Received response: {resp}")
        
        self.tcp.soc.send(str(self.value).encode())
        resp = self.tcp.soc.recv(1024).decode()
        
        self.logger.debug(f"Received response: {resp}")
        if resp != "data received":
           self.logger.error(f"unexcpeted response from server {resp}")
        else:
            self.logger.info("TCP check complete, sending spectra")
            
        self.tcp.soc.send(self.spec.encode())
        
        resp = self.tcp.soc.recv(1024).decode()

    
    #endregion
    
    #region measurement
    def measure(self):
        """
        Performs a measurement using the spectrometer, processes the results, and writes the data to a file.
        This method:
            - Updates the process display to indicate measurement is in progress.
            - Retrieves the selected sample number from the dropdown.
            - Checks if a sample ID is provided; if not, prompts the user.
            - If the spectrometer is ready, attempts to perform a measurement.
            - Collects wavelength and spectral data, formatting them as comma-separated strings.
            - If not connected to the server, prompts the user to enter a sample description.
            - Prepares the data and headers for writing, including sample information and measurement results.
            - Writes the data to a file using the file manager.
            - Handles exceptions by logging errors and reinitializing the spectrometer if measurement fails.
            - Reinitializes the spectrometer state after measurement.
        Raises:
            Exception: If measurement fails, logs the error and resets the spectrometer status.
        """
        self.process_display.set("measuring")
        self.root.update_idletasks()
        self.sample_num = dropdown.instances["samples"].get()
        if self.sample_num == "":
            self.process_display.set("Please select or enter a sample ID")
        else:
            if self.spectrometer.status:
                try:
                    self.spectrometer.measure()
                    
                    str_wvs: str = ""
                    str_spec: str = ""
                    i: int = 0
                    for wv in self.spectrometer.wv:
                        str_wvs += str(wv[0]) + ","
                        str_spec += str(self.spectrometer.spectra[i]) + ","
                        i += 1
                    self.wvs = str_wvs
                    self.spec = str_spec
                    if not self.connected:
                        self.logger.error("Not connected to server, cannot send data, having user enter sample description and op id")
                        self.wait.set(True)
                        self.toggle_id()
                        self.root.wait_variable(self.wait)
            
                        self.wait.set(True)
                        self.toggle_desc()
                        self.root.wait_variable(self.wait)
                    
                    data:list[str | int | float] = [self.sample_num, str(dt.now()), 
                                                    self.description, self.position]
                    for val in self.spec.split(","): 
                        if val != "":data.append(val)
                    
                    headers:list[str] = ["Sample ID", "TIME", "Description", "Position"]
                    
                    for wv in self.wvs.split(","): 
                        if wv != "":headers.append(wv)
                    
                    print(data)
                    self.fmanager.write_data("NIR", headers, data)
                    
                except:
                    self.logger.error("Failed to measure, reinitializing spectrometer")
                    self.spectrometer.status = False
                
                    self.init_spec()
                    
                


    #endregion
    

    #region threading
    
        
        
    #endregion
if __name__ == "__main__":
    logging.info("start from main")
    try:
        SERVER = sys.argv[1]
    except:
        # SERVER = "127.0.0.1" 
        SERVER = "192.168.1.1"
    
    PORT = 5050
    ADDR = (SERVER, PORT)
    
    temp = near_ir_app(SERVER, PORT)
    temp.startApp()

 