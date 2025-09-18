fourppmain:

    This code is the main entry point and core logic for a GUI-based four-point probe measurement application. It begins with importing necessary modules, including custom GUI components, instrument utilities, a dummy four-point probe driver, and standard libraries such as tkinter, sys, datetime, traceback, and logging. The logging is configured to write detailed logs to a file with daily rotation, which is helpful for debugging and tracking application activity.

    The getargsasdict function parses command-line arguments (after the first two) into a dictionary, expecting each argument in the form key=value. This allows flexible configuration when launching the application.

    The main class, four_point_app, encapsulates all application logic. Its constructor initializes various attributes, including the instrument driver, resource strings, data management helpers, and logging. It also sets up TCP connection parameters for communicating with a server.

    The connectClient method attempts to establish a TCP connection to a server, updating the GUI and logging the outcome. If successful, it updates a status label and sends an identification message to the server.

    The startApp method sets up the main Tkinter window, initializes the GUI, connects to the server, and starts the Tkinter event loop. The GUI is built in buildGUI, which creates dropdowns for sample and position selection, status labels, and buttons for measurement and reconnection. It also prepares a separate window for entering or editing sample descriptions.

    The load_dm method initializes the instrument driver and updates the GUI to reflect the driver's status. The tcp_proptocol method manages the protocol for sending measurement metadata and results to the server, including sample number, position, description, and measured value. It handles server responses and prompts the user for input if needed.

    The measure method is the main measurement workflow. It retrieves the selected sample ID, performs a measurement using the instrument driver, calculates the resistance value, and either sends the data to the server (if connected) or prompts the user for a description. All relevant data is saved locally using a file manager. If the driver fails, it attempts to reload it.

    Finally, the script's entry point parses command-line arguments, creates an instance of four_point_app, and starts the application. This structure ensures that the application is modular, user-friendly, and robust against errors in both hardware and network communication.

fourpp:

    This code defines a siglent class that acts as a driver for a four-point probe measurement instrument using the PyVISA library for instrument communication. The class is designed to initialize a connection to the instrument, configure it for resistance measurements, perform measurements, and cleanly shut down the connection.

    In the constructor (__init__), the class sets up various attributes, including the VISA resource manager (rm), the instrument address (inst_addy), and placeholders for measurement results. It also initializes a logger for detailed debugging and status messages.

    The init_driver method establishes a connection to the instrument using the provided VISA address, sets communication parameters (such as read and write terminations), and attempts to communicate with the instrument by sending an identification query (*IDN?). If successful, it sets the status to True. It then configures the instrument for four-wire resistance measurements, sets the sample count, and takes an initial reading to zero the measurement.

    The measure method sends a command to the instrument to perform a measurement (READ?), processes the returned comma-separated string of values, and converts them into a list of floats stored in self.values.

    The quit method closes the instrument connection and the VISA resource manager to ensure resources are released properly.

    In the __main__ block, the code demonstrates how to use the siglent class: it creates an instance, initializes the driver, performs a measurement, prints the measured values, shuts down the connection, calculates the average value, and applies a conversion factor using the convert function. This block serves as a simple test  or usage example for the class.

mainrdt:
    
    This code defines the main structure and logic for an RDT (Rapid Durability Test) measurement application with a graphical user interface (GUI) built using Tkinter. The application is designed to interact with measurement hardware, manage data, and communicate with a server.

    The script starts by importing required modules, including custom GUI components, instrument utilities, the RDT driver, and standard libraries for GUI, system operations, date/time, error handling, and logging. Logging is configured to write detailed logs to a file with daily rotation, which helps with debugging and tracking application activity.

    The core of the application is the rdt_app class. In its constructor, it initializes various attributes for GUI state, measurement data, file management, and logging. It also sets up TCP connection parameters for server communication.

    The connectClient method attempts to establish a TCP connection to a server, updating the GUI and logging the outcome. If successful, it updates a status label and sends an identification message to the server.

    The startApp method sets up the main Tkinter window, initializes the GUI, connects to the server, and starts the Tkinter event loop. The GUI is built in buildGUI, which creates dropdowns for sample and position selection, status labels, and buttons for measurement and reconnection. It also prepares a separate window for entering or editing sample descriptions and displays real-time measurement values (current, T1, T2).

    The load_rdt method initializes the RDT driver and updates the GUI to reflect the driver's status. The tcp_proptocol method manages the protocol for sending measurement metadata and results to the server, including sample number, position, description, and measured value. It handles server responses and prompts the user for input if needed.

    The measure method is the main measurement workflow. It retrieves the selected sample ID, performs a measurement using the RDT driver, collects and structures the measurement data, and saves it locally using a file manager. If the driver fails, it attempts to reload it.

    Finally, the script's entry point parses command-line arguments, creates an instance of rdt_app, and starts the application. This structure ensures the application is modular, user-friendly, and robust against errors in both hardware and network communication.

rdt:

    This code defines the NI_RDT class, which is responsible for controlling National Instruments (NI) hardware to perform RDT (Rapid Durability Test) measurements. The code is structured to support both hardware communication and GUI integration, as well as data logging and plotting.

    The script begins by importing necessary modules, including nidaqmx for hardware control, matplotlib for plotting, and standard libraries for logging, JSON handling, and time management. Logging is set up to write detailed logs to a file with daily rotation, which is useful for debugging and traceability.

    The NI_RDT class constructor (__init__) initializes several attributes:

    Device and DAQ system references, including a dictionary to map device types to names and the local NI system.
    GUI-related variables (root, c1, t1, t2) for real-time display of current and temperature readings.
    Data storage for measurement results.
    Configuration parameters, such as measurement delay, cooling temperature, and the path to the configuration JSON file.
    State definitions for controlling relays (e.g., Off, Heat, Cool, Bias_on).
    Plotting setup using Matplotlib for visualizing temperature and current over time.
    The load_config method loads measurement and device configuration from a JSON file, extracting system-wide settings such as the bias temperature.

    The dev1_init and dev2_init methods initialize the NI DAQ tasks for analog input (current and thermocouples) and digital output (relay control), respectively, based on configuration and detected devices.

    The init_rdt method discovers connected NI devices, initializes them, and sets the system to a safe state. It also reads initial values and updates the GUI.

    The update_gui method updates the GUI with the latest current and temperature readings, formatting the values for display.

    The standard_procedure method implements the main measurement workflow: it preheats the system to a target temperature if necessary, then performs a measurement loop, collecting and plotting data for current and temperatures. The results are stored for later use.

    The cooldown method manages the cooling phase, updating the GUI and plots as the system cools down to a safe temperature.

    The quit method ensures all hardware tasks are safely stopped and closed, returning the system to a safe state.

    The __main__ block demonstrates how to use the class for a simple test: it loads the configuration, initializes the hardware, sets the relay state, waits, and then turns everything off. This structure makes the class suitable for both standalone testing and integration into larger GUI applications.

mainnearir:

    This code defines the main application logic for a Near-Infrared (NIR) measurement system with a graphical user interface (GUI) and TCP client-server communication. The script begins with several imports, including custom GUI and instrument utility modules, as well as standard libraries for logging, date/time, and error handling. Logging is configured to write detailed logs to a file with daily rotation, aiding in debugging and traceability.

    The core of the code is the near_ir_app class, which encapsulates the application's state and behavior. The constructor (__init__) initializes various attributes, such as the spectrometer interface, data management tools, logging, and TCP connection details. It also sets up a logger specific to the class for structured logging throughout the app's lifecycle.

    The connectClient method manages the TCP connection to a remote server, handling both successful and failed connection attempts. It updates the GUI to reflect the connection status and logs relevant events. The startApp method initializes the main Tkinter window, sets up the GUI components, and starts the application's main event loop.

    GUI-related methods like buildGUI, toggle_desc, and get_desc handle user interface construction and interactions, such as sample selection and description entry. The GUI includes dropdowns for sample and position selection, buttons for measurement and reconnection, and status indicators. The description window is managed as a separate Tkinter toplevel window, which can be shown or hidden as needed.

    The init_spec method initializes the spectrometer hardware using a driver from the nearir module, updating the GUI and logging the outcome. The measure method coordinates the measurement process: it retrieves the selected sample, triggers the spectrometer to acquire data, formats the results, and saves them using a file manager. If the application is not connected to the server, it prompts the user for a sample description before proceeding.

    Data exchange with the server is handled by the tcp_proptocol method, which sends metadata, sample information, and measurement results over the TCP connection, following a specific protocol. Throughout the code, error handling and logging are used extensively to ensure robustness and provide feedback to the user.

    The script concludes with a standard Python entry point, which parses command-line arguments for the server address, creates an instance of the application, and starts it. This structure makes the application modular, maintainable, and user-friendly, with clear separation between GUI, hardware interaction, and network communication.


nearir:

    This code defines a Python interface for controlling a Stellarnet spectrometer using a custom driver library. It starts by importing matplotlib.pyplot (though not used in the shown code) and a driver module aliased as sn. The StellarnetError class is a custom exception for handling errors specific to the spectrometer operations. However, its __str__ method tries to access self.message, which is not explicitly set—this could cause an AttributeError if the exception is printed.

    The main class, stellarnet, encapsulates the spectrometer's state and operations. Its constructor (__init__) expects keyword arguments for initialization parameters such as integration time, number of scans to average, smoothing, and timing. These are stored both in a dictionary (self.kwargs) and as individual attributes for convenience. The class also initializes placeholders for the spectrometer device handle (self.spec), device ID, wavelength data, and measured spectra.

    The init_driver method attempts to initialize the spectrometer hardware. It queries the driver for the version, acquires a device handle and wavelength array, sets device parameters, and checks that the hardware accepted the requested settings. If any parameter does not match, it raises a StellarnetError. The method also retrieves an initial spectrum to confirm communication and sets the status flag to indicate success or failure.

    The measure method simply fetches the latest spectrum from the device and stores it. The quit method resets the device and marks the driver as inactive.

    Finally, the script includes a __main__ block that demonstrates how to instantiate the class, initialize the driver, perform a measurement, and clean up. This structure makes the code suitable for both direct execution and import as a module.

    A potential "gotcha" is the handling of the custom exception's message attribute and the assumption that all required keyword arguments are provided; missing any will raise a KeyError during initialization. Additionally, the code assumes the driver functions always return expected types and values, which may not be robust in production environments.


launcher:

    This script is a launcher utility designed to automate environment setup and the execution of Python tools based on the machine's network configuration and command-line arguments. It begins by importing standard libraries for system operations, networking, subprocess management, virtual environment creation, and error handling.

    The spawn_program_and_die function is responsible for starting an external program (typically another Python script) as a separate process and then immediately terminating the current script with a specified exit code. This is useful for handing off control to another script without keeping the launcher running.

    The venv_builder function manages the creation of a Python virtual environment in the current working directory (as .venv). It reads a requirements file (defaulting to constraints.txt), processes its lines (with special handling for a package named "delcom"), and writes a cleaned-up version back to disk. If the virtual environment does not already exist, it creates one, ensures pip is installed, and then installs the required packages using pip.

    The launch function determines which tool or script to run based on the local machine's IP address and a configuration file (config.json). It maps the IP address to a tool name, constructs the appropriate script path, and gathers any additional arguments required by the tool. It then uses the virtual environment's Python interpreter to launch the selected script, passing along the server IP and any extra arguments.

    The script's entry point (if __name__ == "__main__":) parses command-line arguments to decide whether to build the virtual environment, launch a tool, or do both. If no recognized argument is provided, it defaults to launching a tool. Any exceptions encountered during execution are caught and printed with a traceback for easier debugging.

    A key "gotcha" is that the script assumes the presence and correct formatting of config.json and constraints.txt, and that the directory structure for tools matches the expected layout. Additionally, the script is Windows-specific due to hardcoded paths like 'Scripts' and 'python.exe' in the virtual

main:

    This code defnes the main structure for a graphical instrument control suite application. It begins by importing necessary modules, including a custom GUI package, networking, threading, logging, and utility modules. Logging is configured to write detailed logs to a file that rotates daily, which helps with debugging and monitoring.

    The core of the code is the inst_suite class, which manages the application's state, GUI, and instrument connections. In the constructor (__init__), the class initializes placeholders for various instruments (such as spectrometers, shutters, Hall effect, and resistance measurement devices), sets up logging, and loads configuration data from a JSON file. The configuration includes a mapping of tool IPs and a list of tool names, which are used to track and manage instrument connections.

    The setup method is responsible for initializing the TCP server (using a custom multi-server handler), starting the SQL subsystem, and launching the main application and TCP server in separate threads. This allows the GUI and network communication to run concurrently without blocking each other.

    The startApp method creates the main Tkinter window, sets up the GUI layout, checks instrument connections, and starts the Tkinter event loop. The GUI is built in buildGUI, which places labels and status indicators for each instrument and system component (such as network and SQL database) on the window. A "Test" button is provided to manually trigger connection checks.

    The test_connections method checks the status of the network and database connections, updating the GUI to reflect their status (good or bad) using colored icons. It also checks which instruments are currently connected by comparing active sockets to the expected tool list, updating each instrument's status indicator accordingly.

    Finally, the script's entry point creates an instance of inst_suite and calls its setup method, starting the application. This design separates concerns between GUI, networking, and instrument management, making the code modular and easier to maintain. A potential "gotcha" is that the code assumes the presence of certain files (like config.json) and images, and that the custom GUI components behave as expected.

inst_util:

    This code is a comprehensive utility module for managing instrument data collection, database interaction, and network communication in a laboratory or industrial setting. It is organized into several key sections: imports, utility functions, and class definitions.

    The import section brings in a variety of standard and third-party libraries. Notably, it uses pyodbc for database connectivity, socket and select for network communication, and modules like json, csv, and logging for configuration, data handling, and diagnostics. Some imports are marked with #type:ignore to suppress type-checking errors, likely because they are not always used or their types are not strictly enforced.

    The utility functions include strip_space, which processes strings by removing extra spaces and splitting them into a list of words, and parse, which reads and processes data files from a specific instrument (HMS 3000), extracting headers and data in a structured way.

    The class definitions provide the core functionality:

    The sample class tracks the measurement status for a sample across multiple instruments, using a dictionary to record which instruments have completed measurements.
    The sql_client class manages all interactions with a SQL database, including loading configuration, connecting to the database, checking and creating tables, validating column names and values, and writing data. It uses dynamic SQL query construction and includes logic to handle missing columns by altering tables as needed.
    The tcp_multiserver class implements a multi-client TCP server. It manages client connections, receives and processes messages, coordinates with the SQL client, and tracks sample measurement progress. It includes robust error handling and logging, and can gracefully handle client disconnects and server shutdowns.
    The client class provides a simple TCP client for instrument computers to communicate with the server, including methods for connecting, disconnecting, and identifying themselves.
    The FileManager class handles local file storage for instrument data, including automatic deletion of the oldest files when a size limit is exceeded, and writing data to CSV files.
    Overall, the code is designed for extensibility and robustness, with clear separation of concerns between data parsing, database management, network communication, and file handling. It uses Python's type annotations for clarity, and logging for traceability. The design supports multiple instruments and samples, and can adapt to changes in database schema or network conditions.



hall_Script:

    This script automates the workflow for collecting and processing Hall Effect measurement data. It begins by importing necessary modules for system operations, GUI creation, logging, and custom utilities. Logging is configured to write detailed debug information to a time-stamped file, which helps track the script's activity and diagnose issues.

    The script determines the location of the executable and ensures the working directory matches, which is important for consistent file access, especially when running as a packaged executable. The main logic is encapsulated in the silent_hall class, which manages experiment parameters, file tracking, and logging.

    The GUI, built with Tkinter, provides dropdowns for selecting samples and positions, and text boxes for entering descriptions and IDs. The GUI updates dynamically based on server responses, and user actions trigger data collection and transmission. The starApp method launches the GUI for each new data file detected.

    File tracking is managed via a text file, which records the state before and after running the measurement software. The script detects new data files, launches the measurement software, and processes each file through the GUI. For each file, user input is collected and sent to a remote server using a custom TCP protocol, with detailed logging at each step.

    The main block sets up the server connection parameters, ensures the correct working directory, and starts the experiment workflow. The script is robust and extensible, with clear separation between GUI, file management, and network communication. However, it assumes the existence and correct format of several files and directories, which could cause runtime errors if not properly set up.