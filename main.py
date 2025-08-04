
#region imports
from gui_package_cawilvitro import * #type:ignore
import socket
# from queue import Empty #type:ignore
import json
import sys
from instutil import inst_util as iu
import threading
import traceback
from socket import socket
from datetime import datetime as dt
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
        TimedRotatingFileHandler(f'logs\\{date}.log', when = "D", backupCount= 5)
    ]
)
#end region

class inst_suite():
    """
    inst_suite is a class for managing and controlling a suite of scientific instruments via a graphical user interface (GUI) and TCP server.
    Attributes:
        quit (bool): Flag to indicate if the application should quit.
        process_display (tk.StringVar): Variable to display process status in the GUI.
        NIR, CTR, UTR: Instrument handles for spectrometers (Near-IR, Coated/Uncoated Transmission and Reflection).
        CS, US: Instrument handles for coated and uncoated side shutters.
        hall: Instrument handle for Hall effect measurement.
        light: Instrument handle for NIR light control.
        R_D_T: Instrument handle for RDT measurement.
        CRM, CLRM: Instrument handles for contact and contactless sheet resistance.
        logger (logging.Logger): Logger for the application.
        host (str): Host IP address for TCP server.
        port (int): Port number for TCP server.
        ADDR (tuple): Address tuple for TCP server.
        configpath (str): Path to configuration file.
        toolip (dict): Mapping of tool names to IP addresses.
        tools (list): List of tool IP addresses.
        tcphandler (iu.tcp_multiserver): TCP server handler instance.
        appThread, tcpThread (threading.Thread): Threads for application and TCP server.
        root (tk.Tk): Main Tkinter application window.
        net_stat (bool): Network connection status.
        db_stat (bool): Database connection status.
    Methods:
        __init__():
            Initializes the inst_suite class, sets up logging, loads configuration, and prepares instrument attributes.
        setup():
            Sets up and starts the main application and TCP server threads.
        startApp():
            Initializes and starts the Tkinter GUI application, builds the GUI, and tests instrument connections.
        endApp(event):
            Gracefully shuts down the application and closes instrument connections.
        buildGUI(root):
            Constructs the GUI layout and places instrument status labels and control buttons.
        test_connections():
            Checks the status of network, database, and instrument connections, and updates the GUI accordingly.
    """
    #region app init
    def __init__(self):
        
        self.quit = False
        self.process_display = None

        #spectrometers
        self.NIR = None
        self.CTR = None  #coated side transmission and reflection spectrometer
        self.UTR = None #uncoated side transmission and reflection

        #light contorls

        self.CS = None #coated side shutter
        self.US = None #uncoated side shutter


        #Hall effect
        self.hall = None

        #light control for NIR
        self.light = None

        #RDT 
        self.R_D_T = None

        #resistances
        self.CRM = None #contact sheet R
        self.CLRM = None #contactless sheet R
        
        #logging
        class_name = str(type(self))
        name = class_name.split(" ")[-1][:-1].replace("'", "") #i know convoluted but it gives me the full stack trace
        
        self.logger = logging.getLogger(name)
        self.logger.info("Server initalized")
        
        #tcp vars
        try:
            self.host = sys.argv[1]
        except:
            self.host = "192.168.1.1"
            
        self.port = 5050
        self.ADDR = (self.host, self.port)
        self.configpath = 'config.json'
        with open(self.configpath , 'r') as file:
            self.toolip:dict[str,str] = json.load(file)['Tool_ip']
        self.tools:list[str] = list(self.toolip.values())
        
        #sql stuff app thread will handle sql as it is not continously running
          
    def setup(self) -> None:
        """
        Initializes and starts the main application threads.
        This method sets up the necessary threads for the main application, including:
        - A TCP server handler for managing instrument communication.
        - The main application thread.
        - (Optionally) an instrument manager thread (currently commented out).
        The threads are set as daemons and started. The method then waits for the threads to complete using `join()`.
        Side Effects:
            - Changes the current working directory (cwd) to fix potential issues (implementation not shown).
            - Starts and manages background threads for application and TCP server.
        Raises:
            Any exceptions raised during thread startup or TCP handler initialization.
        """
        
        # self.message: Queue[Any] = Queue(maxsize=1)
        # self.response: Queue[Any] = Queue(maxsize=1)
        
        #setting up tcp server and getting instruments
        self.tcphandler: iu.tcp_multiserver = iu.tcp_multiserver(self.configpath, self.host, self.port, self)#, self.message, self.response)
        self.tcphandler.SQL_startup()
        
        self.appThread = threading.Thread(target=self.startApp, args=())
        self.tcpThread = threading.Thread(target=self.tcphandler.server, args=())
        # self.insturmentManagerThread = threading.Thread(target=self.test, args=())
        
        self.appThread.daemon = True
        self.tcpThread.daemon = True
        # self.insturmentManagerThread.daemon = True
        
        #starting threads
        self.appThread.start()
        self.tcpThread.start()
        # self.insturmentManagerThread.start()
        
        self.appThread.join()
        self.tcpThread.join()
        # self.insturmentManagerThread.join()
        
        #cwd to fix issues         
    
    #endregion
    #region application control   
   
    def startApp(self):
        """
        Initializes and starts the Tkinter application.
        This method sets up the main application window, configures its title and size,
        binds the Escape key and window close event to the application shutdown handler,
        initializes the process display variable, builds the GUI, tests instrument connections,
        and starts the Tkinter main event loop.
        Side Effects:
            - Creates and displays the main Tkinter window.
            - Initializes GUI components and process display.
            - Tests instrument connections before starting the main loop.
            - Binds event handlers for application shutdown.
        """
        
        self.root: tk.Tk = tk.Tk() 
        self.root.title("Insturment Control Suite")
        self.root.geometry("430x485")
        self.root.bind("<Escape>", self.endApp) #type: ignore
        self.root.protocol("WM_DELETE_WINDOW",partial(self.endApp, None))
        self.process_display = tk.StringVar() 
        self.process_display.set("Booting")
        self.root.update_idletasks()
        self.buildGUI(self.root)
        self.test_connections()
        self.root.mainloop()
        
         #checks inst connections before booting up tcp server and other 
        pass

    def endApp(self, event: Any):
        """
        Handles the termination of the application.

        This method sets the quit flag to True, signals the TCP handler to stop,
        closes the main application window, and exits the program.

        Args:
            event (Any): The event object that triggered the application shutdown.
        """
        self.quit = True
        self.tcphandler.quit()
        self.root.quit()
        sys.exit(0)
    #endregion
    
    #region GUI building
    def buildGUI(self, root: tk.Tk) -> None:
        """
        Constructs and places all GUI components (labels and buttons) on the given Tkinter root window.
        This method initializes a set of custom StandardLabel and StandardButtons widgets, each associated with a specific image and placed at fixed coordinates within the root window. It also resets any existing StandardLabel instances before building the new interface. The labels represent different system components and their statuses, while a button is provided to trigger connection tests.
        Args:
            root (tk.Tk): The root Tkinter window where the GUI components will be placed.
        Side Effects:
            Modifies the GUI by adding/removing widgets to/from the root window.
        """

        StandardLabel.remove(None)
        
        StandardLabel (
            "hall",
            root,
            image = TkImage("hall_label", r"images\hall_label.png").image
        ).place(x = 50, y = 5)
        
        StandardLabel (
            "hall_status",
            root,
            image = TkImage("hall_status", r"images\Status_Bad.png").image
        ).place(x = 198, y = 10)
        
        StandardLabel (
            "4pp",
            root,
            image = TkImage("4pp_label", r"images\4pp_label.png").image
        ).place(x = 50, y = 75)
        
        StandardLabel(
            "fourpp_status",
            root,
            image = TkImage("fourpp_status", r"images\Status_Bad.png").image
        ).place(x = 198, y = 80)
        
        StandardLabel (
            "rdt",
            root,
            image= TkImage("rdt_label", r"images\rdt_label.png").image
        ).place(x = 50, y = 145)
        
        StandardLabel(
            "rdt_status",
            root,
            image = TkImage("rdt_status_bad", r"images\Status_Bad.png").image
        ).place(x = 198, y = 150)
        
        StandardLabel (
            "nearir",
            root,
            image= TkImage("nearir_label", r"images\nir_label.png").image
        ).place(x = 50, y = 215)
        
        StandardLabel (
            "nearir_status",
            root,
            image= TkImage("nearir_status", r"images\Status_Bad.png").image
        ).place(x = 198, y = 220)
        
        StandardLabel (
            "SQL",
            root,
            image= TkImage("SQL_label", r"images\sql_label.png").image
        ).place(x = 50, y = 350)
        
        StandardLabel (
            "SQL_status",
            root,
            image= TkImage("SQL_status", r"images\Status_Bad.png").image
        ).place(x = 210, y = 355)
        
        StandardLabel (
            "Network",
            root,
            image= TkImage("Net_label", r"images\network_label.png").image
        ).place(x = 50, y = 400)
        
        StandardLabel (
            "Net_status",
            root,
            image= TkImage("Net_status", r"images\Status_Bad.png").image
        ).place(x = 210, y = 405)
        
        StandardButtons(
            "Test",
            root,
            image = TkImage("Test", r"images\test_connections.png").image,
            command = self.test_connections,
        ).place(x = 50, y = 300)
    
    #endregion
    #region inst manager
    
    def test_connections(self):
        """
        Tests and updates the status of network, database, and instrument connections.
        This method performs the following actions:
        1. Checks the status of the internet and database connections using `self.tcphandler`.
        2. Updates the GUI to reflect the network and database connection status by displaying appropriate status images.
        3. Checks the connection status of each instrument by comparing the list of connected sockets to the expected tools.
        4. Updates the GUI to reflect the connection status of each instrument.
        5. Handles cases where a tool is not integrated into the front end by catching `KeyError` and printing a message.
        6. Refreshes the GUI to show the updated statuses.
        Assumes the existence of:
        - `self.tcphandler`: An object managing TCP connections and statuses.
        - `self.root`: The root GUI window.
        - `StandardLabel`: A GUI label class with an `instances` dictionary for status labels.
        - `TkImage`: A class for loading images.
        - `self.toolip`: A mapping from IP addresses to tool names.
        - `self.tools`: A list of tool names.
        """
        # StandardLabel.instances["fourpp_status"].configure(image = TkImage("fourpp_status", r"images\Status_Bad.png").image)

        # first testing internet connections
        self.tcphandler.connections()
        print("Testing connections")
        self.net_stat = self.tcphandler.network_status
        self.db_stat = self.tcphandler.db_status
        
        if self.net_stat:
            StandardLabel (
                "Net_status",
                self.root,
                image= TkImage("Net_status", r"images\Status_Good.png").image
            ).place(x = 210, y = 405)
        else:
            StandardLabel (
                "Net_status",
                self.root,
                image= TkImage("Net_status", r"images\Status_Bad.png").image
            ).place(x = 210, y = 405)

        if self.db_stat:
            StandardLabel (
                "SQL_status",
                self.root,
                image= TkImage("SQL_status", r"images\Status_Good.png").image
                ).place(x = 210, y = 355)
        else:
            StandardLabel (
                "SQL_status",
                self.root,
                image= TkImage("SQL_status", r"images\Status_Bad.png").image
            ).place(x = 210, y = 355)
        
        #testing instrument connections
        conc_clients: list[socket] = self.tcphandler.connected_sockets
        conc_tools: list[str] = [self.toolip[soc.getpeername()[0]] for soc in conc_clients]

        for tool in self.tools:
            try:
                if tool in conc_tools:
                    StandardLabel.instances[f"{tool}_status"].configure(image = TkImage(f"{tool.lower()}_status", r"images\Status_Good.png").image)
                else:
                    StandardLabel.instances[f"{tool}_status"].configure(image = TkImage(f"{tool.lower()}_status", r"images\Status_Bad.png").image)
            except KeyError:
                print(f" {tool} not integrated into Front end")
        self.root.update()
    # endregion  


if __name__ == "__main__":
    try:
        temp = inst_suite()
        temp.setup()
    except Exception as e:
        temp.logger.error(traceback.format_exc())
