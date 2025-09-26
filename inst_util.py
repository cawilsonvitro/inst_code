#region imports
import pyodbc
import json
import re
import time
import socket 
import select
from multiprocessing import Process, Queue #type:ignore
from queue import Empty #type:ignore
from typing import Any #type:ignore
import json #type:ignore
from datetime import datetime as dt
import traceback
import logging
import os
import csv
#endregion 
#region logging
#endregion
#region functions

def get_args_as_dict(sys_args:str) -> dict[str, str]:
    """
    Converts a list of command-line arguments in the form "key=value" into a dictionary.
    Args:
        sys_args (str): A list of strings, each formatted as "key=value".
    Returns:
        dict[str, str]: A dictionary mapping each key to its corresponding value.
    Raises:
        IndexError: If any argument does not contain an '=' character.
        ValueError: If the input is not iterable or not formatted as expected.
    Example:
        >>> get_args_as_dict(["foo=bar", "baz=qux"])
        {'foo': 'bar', 'baz': 'qux'}
    """
    argsin = [
    i.split("=") for i in sys_args
    ]
    dictout = {}
    for t in argsin:
        dictout[t[0]] = t[1]

    return dictout


def strip_space(string_in: str) -> list[str]:
    """
    Removes spaces from the input string and returns a list of words.
    Args:
        string_in (str): The input string to process.
    Returns:
        list[str]: A list of words from the input string, with spaces removed.
    Example:
        >>> strip_space("hello world  test")
        ['hello', 'world', 'test']
    """

    no_space: list[str] = []
    word = ""
    i = 0
    for char in string_in:
        
        if char  != " ":
            word += char
        else:
            if word != "":
                no_space.append(word)
            word = ""

        i += 1
    
    if word != "":
        no_space.append(word)
     
    return no_space

def parse(filepath:str) -> tuple[list[str],list[str]]:
    """
    Parses a file to extract header and data information.
    The function reads the specified file line by line, processes each line to separate headers and data,
    and performs specific transformations on the headers between indices 19 and 28. It also removes or modifies
    certain header entries based on their positions.
    Args:
        filepath (str): The path to the file to be parsed.
    Returns:
        tuple[list[str], list[str]]: A tuple containing two lists:
            - The first list contains the processed headers.
            - The second list contains the extracted data entries.
    """


    i = 0
    headers: list[str]= []
    datas: list[str] = []

    temp: list[str] = []


    with open(filepath,"r") as f:
        lines = f.readlines()
    for line in lines:
        if line.find("----") == -1 and line.find("===") == -1:
            temp = strip_space(line.strip())
            if temp != []:
                #dealing with non- numeric data
                if i == 0:
                    for obj in temp:headers.append(obj)
                if i == 1:
                    for obj in temp:datas.append(obj)
                if i != 0 and i != 1:
                    try:
                        float(temp[0])
                        for obj in temp:datas.append(obj)
                    except ValueError:
                        for obj in temp:headers.append(obj)

            i += 1
    # 19 to 28 need to be fixed 29 and 30 need to be removed


    i = 19
    plus = headers[29][:-1]
    minus = headers[30][:-1]
    last = headers[-1]
    new = headers[:29]

    for header in headers[19:29]: #type:ignore
        new.append(headers[i] + minus)
        new[i] =  headers[i] + plus
    
        i += 1

    new.append(last)  
    return new,datas

#endregion

#region classes

class sample():
    """
    Represents a sample and tracks its measurement status and associated instruments.
    Attributes:
        id (str): Identifier for the sample.
        description (str): Description of the sample.
        insts (dict): Dictionary tracking whether each instrument ('fourpp', 'nearir', 'rdt', 'hall') has been used.
        test (bool): If True, indicates that the sample has been tested regardless of instrument status.
    Methods:
        check() -> bool:
            Checks if all instruments have performed a measurement or if the test flag is set.
            Returns True if all measurements are done or test is True, otherwise False.
    """
    def __init__(self):
        """_summary_         main use is to keep track of sample measurements and current sample id\n
        keeps track of what inst has been used using a dict
        """
        
        self.id:str = ""
        
        self.description: str = "None"
        
        self.insts = {
            'fourpp': False,
            "nearir": False,
            "rdt": False,
            "hall": False,
        }
        self.test = False

    def check(self) -> bool:
        """_summary_ checks if instrument has a measurement yet

        Returns:
            bool:  True if measurement is done\n
            false if measurement is not done \n
        """
        if self.test: 
            return True

        for key in self.insts.keys():
            if not self.insts[key]:
                return False
        return True

class sql_client():
    """
    A client class for managing SQL database connections, table creation, column validation, and data insertion
    using configuration from a JSON file.
    Attributes:
        host (str): SQL server host address.
        user (str): Username for SQL server authentication.
        pw (str): Password for SQL server authentication.
        db (str): Database name to connect to.
        config_path (str): Path to the configuration JSON file.
        config_db (dict[str, str]): Database configuration loaded from the config file.
        config_tools (dict[str, str]): Tool IP configuration loaded from the config file.
        hall_sys (str): Hall system identifier.
        sql (pyodbc.Connection): Active SQL connection object.
        cursor (pyodbc.Cursor): Cursor object for executing SQL queries.
        tools (list[str]): List of tool names from the configuration.
        tables (list[str]): List of table names in the database.
        missing_col_error (str): Error code for missing columns.
        illegal_char (list[str]): List of illegal characters for column names.
        illegal_val (list[str]): List of illegal values for data validation.
        hall_cols (list[str]): List of hall column names.
        col_flags (list[bool]): Flags for column checks.
        prefixes (dict[str, str]): Prefixes for table columns.
        logger (logging.Logger): Logger instance for the class.
    Methods:
        __init__(config_path: str) -> None:
            Initializes the sql_client instance with the given configuration path.
        load_config():
            Loads database and tool configuration from the JSON config file.
        connect():
            Establishes a connection to the SQL server and ensures the target database exists.
        check_columns(table: str, columns: str) -> None:
            Checks if the specified columns exist in the given table, and adds them if missing.
        table_query_builder(tool: str, prefix: str, cols: list[str], data_types: list[str], data_sizes: list[str]) -> str:
            Builds a SQL query string for creating a table with the specified columns and data types.
        check_tables():
            Checks for the existence of required tables and creates them if they do not exist.
        check_for_illegals(col_name: str) -> bool:
            Checks if the column name contains any illegal characters.
        check_val(val: str) -> bool:
            Checks if the value contains any illegal values.
        write(table: str, values: list[list[str]]):
            Inserts a row of data into the specified table, adding prefixes to column names as needed.
        quit():
            Closes the SQL database connection.
    """
    
    def __init__(self, config_path: str) -> None:
        """_summary_ init sql class for connecting to sql database

        Args:
            config_path (str): path to config.json
        """
        self.host: str = ""
        self.user: str = ""
        self.pw: str = ""
        self.db: str = ""
        
        #config 
        self.config_path:str = config_path
        self.config_db:dict[str, str] = {
            
            }
        self.config_tools:dict[str, str] = {
            
        }
        self.hall_sys: str = ""
        #server connection
        self.sql: pyodbc.Connection
        self.cursor: pyodbc.Cursor
        #for building tables
        
        #sql querries
        self.tools:list[str] = []
        self.tables: list[str] = []
        self.missing_col_error:str = "207"
        self.illegal_char: list[str] = ["+","(",")","-",","]
        self.illegal_val: list[str] = ["hour", "second", "minute", "min", "-", ":"]
        self.hall_cols: list[str] = []
        
        #col check flags
        self.col_flags = []
        
        
        
        #int prefixes
        self.prefixes: dict[str,str] = {
            
        }
        #logging
        class_name = str(type(self))
        name = class_name.split(" ")[-1][:-1].replace("'", "")
        self.logger = logging.getLogger(name)
        self.logger.info("Connected to Server")
    
    def load_config(self):
        """
        Loads configuration settings from a JSON file specified by `self.config_path` and initializes
        various instance attributes for database and tool configuration.
        The method performs the following actions:
            - Reads and parses the JSON configuration file.
            - Extracts and assigns database configuration for "fourpp" and general database settings.
            - Sets up tool IPs, tool prefixes, and system information.
            - Initializes connection parameters such as host, user, password, driver, and database name.
            - Populates lists of tool names, default column names and sizes, and four-point probe column names and sizes.
            - Initializes column flags for each tool.
        Raises:
            FileNotFoundError: If the configuration file does not exist.
            KeyError: If expected keys are missing in the configuration file.
            json.JSONDecodeError: If the configuration file is not valid JSON.
        """

        with open(self.config_path, 'r') as file:
            config: dict[str, dict[str, str]]  = json.load(file)
            self.fpp_db_config = config["fourpp"]["db"]
            print(self.fpp_db_config)
            self.hall_sys: str = config["Hall"]["sys"]
            self.config_db: dict[str,str] = config["Database_Config"]
            self.config_tools: dict[str,str] = config["Tool_ip"]
            self.prefixes: dict[str,str] = config["Tool_pre"]
        #connection string from files
        self.host = self.config_db["host"]
        self.user = "pylocal"
        self.pw =  "pyvitro"
        self.driver = self.config_db["driver"]
        self.db = self.config_db["db"]
        #tool names from file
        self.tools = list(self.config_tools.values())
        #default col from sys
        col_dict = self.config_db["default_col"]
        self.def_col_names = []
        self.def_col_sizes = []
        self.fpp_col_names = []
        self.fpp_col_sizes = []
        
        for key, value in col_dict.items():
            self.def_col_names.append(key)
            self.def_col_sizes.append(value)
        self.col_flags = [False] * len(self.tools)
        for key, value in self.fpp_db_config.items():
                self.fpp_col_names.append(key)
                self.fpp_col_sizes.append(value)
    def connect(self):
        """
        Establishes a connection to the SQL database server using the provided credentials.
        If the specified database does not exist, it creates the database.
        Reconnects to the server with the target database selected.
        Steps:
            1. Connects to the SQL server using host, user, driver, and password.
            2. Retrieves the list of existing databases.
            3. Checks if the target database exists; if not, creates it.
            4. Closes the initial connection.
            5. Reconnects to the server with the target database.
            6. Initializes the cursor for executing SQL commands.
        Attributes Modified:
            self.sql: The active database connection.
            self.cursor: The cursor for executing SQL statements.
            self.dbs: List of existing database names.
            self.closed: Connection closed status.
        """

        self.sql = pyodbc.connect(
            host = self.host,
            user = self.user,
            driver = self.driver,
            password = self.pw,
            autocommit = True
        )
        self.cursor = self.sql.cursor()
        
        # #checking for db then connecting
        
        self.cursor.execute("SELECT name FROM sys.databases;")
        
        self.dbs = [x[0] for x in self.cursor]
        self.cursor.commit()
         
        
        if self.db not in self.dbs:
            self.cursor.execute(f"CREATE DATABASE {self.db}")
        self.cursor.commit()
        self.sql.close()
        
        self.sql = pyodbc.connect(
            host = self.host,
            user = self.user,
            password = self.pw,
            driver = self.driver,
            database = self.db,
            autocommit = False
        )

        self.cursor = self.sql.cursor()
        
        self.closed = self.sql.closed
        
    def check_columns(self, table: str , columns: str) -> None:
        """
        Checks if the specified columns exist in the given table. If any columns are missing,
        attempts to add them to the table with a default type of VARCHAR(255). This needs to be fixed to deal with different data types
        Args:
            table (str): The name of the table to check.
            columns (str): A comma-separated string of column names to check for existence.
        Raises:
            pyodbc.Error: If a database error occurs that is not related to missing columns.
        """

        try:
            # print("FROM DB HANDLER")
            # print(columns)
            column_check: str = f"SELECT "#\"{columns}\" FROM {table}"
            temp_list = columns.split(",")
            for column in temp_list:
                column_check += f"\"{self.prefixes[table]}_{column}\", "
            column_check = column_check[:-2] + f" FROM {table}"
                
            self.cursor.execute(column_check)
            self.cursor.fetchall()
            
        except pyodbc.Error as e:
            error: str = str(e)
            positions = [match.start() for match in re.finditer(self.prefixes[table]+"_", error)]
            query = f"ALTER TABLE {table} ADD "
            cols_to_add: list[str] = []
            if len(positions) != 0:
                for pos in positions:
                    end = error[pos:].index("\'") + pos
                    val = f"{error[pos:end]}"
                    cols_to_add.append(val)
                
                
                i: int = 0
                for col in cols_to_add:
                    pref:str = f"{self.prefixes[table]}_"
                    if pref not in col:
                        cols_to_add[i] = f"\"{self.prefixes[table]}_{cols_to_add[i]}\" VARCHAR(255)"
                    else:
                        cols_to_add[i] = f"\"{cols_to_add[i]}\" VARCHAR(255)"
                    #dealing with ending chars we don't like
                    if ":" in cols_to_add[i]:
                        idx = cols_to_add[i].index(":")
                        cols_to_add[i] = cols_to_add[i][:idx] + cols_to_add[i][idx+1:]
                    
                    i += 1

                query += ",".join(cols_to_add)
   
                # print(f"adding {cols_to_add}")
                #  \"{col_to_add}\" VARCHAR(255)"
                # print(query)
                self.cursor.execute(query)
                self.sql.commit()
    
    def table_query_builder(self, tool:str, prefix:str, cols:list[str], data_types:list[str], data_sizes:list[str]) -> str:
        """
        Builds a SQL CREATE TABLE query string based on provided column definitions.
        Args:
            tool (str): The name of the table to be created.
            prefix (str): The prefix to prepend to each column name.
            cols (list[str]): A list of column names.
            data_types (list[str]): A list of data types for each column. If the data type already contains parentheses (e.g., "VARCHAR(255)"), it is used as is.
            data_sizes (list[str]): A list of data sizes for each column (currently unused in the function).
        Returns:
            str: The constructed SQL CREATE TABLE query string.
        """

        query_pre:str = f"CREATE TABLE {tool} ("

        query_as_list = []
        i = 0 
        print(data_types,cols)
        for col in cols:
            if "(" in data_types[i] and ")" in data_types[i]:temp = f"{prefix}_{col} {data_types[i]}"
            else: 
                temp = f"{prefix}_{col} {data_types[i]}({data_types[i]})"
            query_as_list.append(temp)
            i += 1
            
            
        query_col = ",".join(query_as_list)
        query = f"{query_pre} {query_col})"

        return query

    
                        
    
    def check_tables(self):
        """
        Checks the existence of required tables in the database and creates any missing tables based on predefined schemas.
        This method performs the following steps:
        1. Logs the start of the table checking process.
        2. Retrieves the list of existing base tables from the database and stores their names.
        3. Iterates over the list of tools (excluding "host" and "testing") and checks if each tool's table exists.
        4. For missing tables, constructs and executes a CREATE TABLE query using default column names and sizes.
           - If the tool is "fourpp", additional columns specific to "fourpp" are appended.
        5. Commits the changes to the database.
        6. If the system is configured for "HMS" hall system, refreshes the table list and ensures the "hall" table has the required columns by calling `check_columns`.
        Note:
            - Uses a 1-second delay after committing changes to ensure SQL changes are applied.
            - Assumes existence of attributes: `logger`, `cursor`, `sql`, `def_col_names`, `def_col_sizes`, `tools`, `fpp_col_names`, `fpp_col_sizes`, `table_query_builder`, `prefixes`, `hall_sys`, `check_columns`, and `hall_cols`.
        """

        self.logger.info("checking tables and building missing")
        temp: pyodbc.Cursor|None = None
        temp = self.cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
        self.tables = [x[2] for x in temp]
        hall_name:str = ""
        cols = self.def_col_names.copy()#["sample_id", "pos", "time", "description"]
        sizes = self.def_col_sizes.copy()#["255"] * 4
        #sizes.append("8000")
        #data_types = ["VARCHAR"] * 4
        #removing debugging and hosting tools
        tools = [i for i in self.tools if i != "host" and i != "testing"]
        
        for tool in tools:
            cols = self.def_col_names.copy()
            sizes = self.def_col_sizes.copy()
            
            if tool == "hall":hall_name = tool #seems unneeded but the var is used
            
            if tool not in self.tables:
                if tool == "fourpp":
                    k = 0
                    for name in self.fpp_col_names:
                        cols.append(name)
                        sizes.append(self.fpp_col_sizes[k])
                        k += 1
                        
                query = self.table_query_builder(tool,self.prefixes[tool],cols,sizes,[])
                self.cursor.execute(query)

        self.sql.commit()
        
        time.sleep(1) #wait for sql changes to come in
        if self.hall_sys == "HMS":
            temp = self.cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
            self.tables = [x[2] for x in temp]
            self.hall_cols,_ = parse(r"sample_file.txt")
            # self.hall_cols = ['DATE', 'User_Name', 'Sample_Name', 'I(mA)', 'B', 'D', 'D_T', 'MN', 'T(K)', 'Nb', 'u', 'rho', 'RH', 'RHA', 'RHB', 'NS', 'SIGMA', 'DELTA', 'ALPHA', 'Vab+I', 'Vbc+I', 'Vac+I', 'Vmac+I', 'V-mac+I', 'Vcd+I', 'Vda+I', 'Vbd+I', 'Vmbd+I', 'V-mbd-I', 'V-mbd+I' 'Vab-I', 'Vbc-I', 'Vac-I', 'Vmac-I', 'V-mac-I', 'Vcd-I', 'Vda-I', 'Vbd-I', 'Vmbd-I', 'Rs']
            self.check_columns(hall_name, (",").join(self.hall_cols))                    
        
        #checking that extra cols got added for other 4 tools
       


    def check_for_illegals(self, col_name: str) -> bool:
        """
        Checks if the given column name contains any illegal characters.
        Args:
            col_name (str): The column name to check for illegal characters.
        Returns:
            bool: True if the column name does not contain any illegal characters, False otherwise.
        """

        for char in self.illegal_char:
            if col_name.find(char) != -1:
                return False
        return True
    
    def check_val(self, val: str) -> bool:
        """
        Checks if the given string `val` contains any illegal characters.
        Iterates through the list of illegal characters defined in `self.illegal_val`
        and returns False if any of these characters are found in `val`. Otherwise,
        returns True.
        Args:
            val (str): The string value to be checked.
        Returns:
            bool: True if `val` does not contain any illegal characters, False otherwise.
        """

        for char in self.illegal_val:
            if val.find(char) != -1:
                return False
        return True
    
    def write(self, table: str, values : list[list[str]]):
        """
        Inserts a new row into the specified table with the provided column-value pairs.
        Args:
            table (str): The name of the table to insert data into.
            values (list[list[str]]): A list of [column, value] pairs representing the data to insert.
                Each inner list should contain two strings: the column name and its corresponding value.
        Notes:
            - Column names may be prefixed based on the table and internal logic.
            - The method checks for illegal characters in column names and values.
            - The SQL query is constructed dynamically and executed using the class's cursor.
            - The transaction is committed after execution.
        """

        # self.cursor.execute("insert into fourpp(fpp_time, fpp_sample_id, fpp_resistance) values ('12:30', '30', '123')")
        # self.cursor.commit()
        #values is going to be formatted as         
        # values = [[col1, val1] , [col2, val2]]
        query = f"insert into {table}("
        end = "("
        for value in values:
            if self.prefixes[table] not in value[0]:
                if self.check_for_illegals(value[0]):
                    query += f"{self.prefixes[table]}_{value[0]}, " #building query 
                else:
                    query += f"\"{self.prefixes[table]}_{value[0]}\", "
            else:
                if self.check_for_illegals(value[0]):
                    query += f"{value[0]}, " #building query 
                else:
                    query += f"\"{value[0]}\", "#building query 
            
            if self.check_val(value[1]):
                end += f"\'{value[1]}\',"
            else:
                end += f"\'{value[1]}\', "

        # print("VALUESSS:",end[-1])
        while end[-1] != " " and end[-1] != "," and end[-1] != "":
            end = end[:-1]
        end = end[:-1]
        # print("VALUESSS:",end[-1])


        
        query = query[:-2] 

        query = query + ")" + " values " + end + ")"
        print(query)
        self.cursor.execute(query)
        self.sql.commit()
       
    def quit(self):
        '''
        ends connection to sql db
        '''
        #closes
        self.sql.close()

class tcp_multiserver():
    """
    tcp_multiserver is a class for handling multithreaded TCP server operations, managing communication with multiple instrument computers, SQL servers, and a GUI interface. It supports multiple client connections, tracks sample measurements, and coordinates data exchange and logging.
    Attributes:
        ADDR (tuple[str, int]): Server IP address and port.
        max_connections (int): Maximum number of allowed client connections.
        server_socket (socket.socket): Main server socket.
        connected_sockets (list[socket.socket]): List of currently connected client sockets.
        starttime (float): Server start time.
        display (Any): GUI interface for displaying information.
        client_data (str): Data received from clients.
        SQL (sql_client): SQL client for database operations.
        samples (list[sample]): List of sample objects being tracked.
        read_to_read (list[socket.socket]): Sockets ready for reading.
        retries (int): Number of server restart attempts.
        network_status (bool): Status of network connectivity.
        db_status (bool|None): Status of database connectivity.
        logger (logging.Logger): Logger for server events.
        config (dict[str, str]): Configuration mapping tool names to IPs.
        prefixes (dict[str, str]): Prefixes for tool data columns.
    Methods:
        __init__(config, ip, port, gui, max_connections=5): Initializes the server with configuration, network, and GUI settings.
        get_sample(tool, sample_id): Retrieves or creates a sample object for a given tool and sample ID.
        SQL_startup(): Initializes and connects to the SQL database.
        connections(host="8.8.8.8", port=53, timeout=30): Checks network and database connectivity.
        all_sockets_closed(): Closes the server and displays connection duration.
        active_client_sockets(): Prints information about currently connected clients.
        serve_client(current_socket): Handles incoming messages from a client socket.
        update(current_socket, tool): Sends a list of pending samples to a client tool.
        disconnect_socket(current_socket): Disconnects a client socket and updates the active list.
        send_meta(current_socket, tool): Handles metadata exchange for a sample with a client.
        meas_prot(current_socket, tool, t): Handles measurement protocol and data storage for a client tool.
        get_id(current_socket): Sends the tool ID to the client.
        server(): Main server loop for accepting and serving client connections.
        quit(): Closes the server and disconnects from the SQL database.
    """
    def __init__(self, config:str, ip:str, port:int, gui:Any, max_connections:int = 5):#, bus_out:"Queue[Any]" , bus_in:"Queue[Any]", max_connections:int = 5):
        """_summary_        class for handing multithreaded operation of a tcp server, handles communication to all intrument computer,\n
        to sql servers, and displaying information on the gu

        Args:
            config (str): path to config.json
            ip (str): ip to launch the server on
            port (int): port to open for server please use a port > 5000
            bus_out (Queue[Any]): a queue to communicate between server and other processes
            bus_in (Queue[Any]): used to communicate into server from other processes
            max_connections (int, optional): number of connections allowed to server. Defaults to 5.
        """
        self.ADDR: tuple[str, int] = (ip, port)
        print(self.ADDR)
        self.max_connections: int = max_connections
        self.server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected_sockets: list[socket.socket] = []  # list of the client sockets being connected
        
        self.starttime: float
        
        self.display = gui
        self.gui_available: bool = False
        
        if self.display is not None:
            self.gui_available = True
        
        # print("From TCP SERVER:",self.display.teststr)
        #data managementjson
        self.client_data: str
        #self.bus_out: "Queue[Any]" = bus_out
       # self.bus_in: "Queue[Any]" = bus_in
        self.SQL: sql_client = sql_client("config.json")
        self.samples: list[sample] = []  # list of samples
        
        #client ids
        self.read_to_read: list[socket.socket] = []
        self.tool: str = ""
        
        #connection flags
        self.retries: int = 0
        self.network_status: bool = False
        self.db_status: bool|None = False
        
        #logging
        class_name = str(type(self))
        name = class_name.split(" ")[-1][:-1].replace("'", "")
        
        self.logger = logging.getLogger(name)
        self.logger.info("Server initalized")


        self.logger.debug(f"Opening config from{config}")
        with open(config, 'r') as file:
            config_dict: dict[str,dict[str,str]] = json.load(file)
            self.config: dict[str, str] = config_dict['Tool_ip']
            self.prefixes: dict[str, str] = config_dict['Tool_pre'] 
        self.logger.debug("Loaded config")
        return
        
    def get_sample(self, tool, sample_id):
            self.logger.debug(f"searching for {sample_id}")
            found:bool = False
            i: int = 0
            current_sample:sample
            for samp in self.samples:
                if samp.id == sample_id:
                    current_sample = samp
                    samp.insts[tool] = True
                    found = True
                    insts = list(samp.insts.values())
                    if all(insts):
                        self.logger.debug(f" all measurements for {sample_id}, removing sample from local mem")
                        del self.samples[i]
                    self.logger.debug(f"found {sample_id}")
                    break
                i += 1
            if not found:
                self.logger.debug(f"{sample_id} not found creating new sample object")
                temp_samp:sample = sample()
                temp_samp.id = sample_id
                temp_samp.insts[tool] = True
                self.samples.append(temp_samp)
                current_sample = temp_samp
            return current_sample

    
    def SQL_startup(self):
        '''
        starts up sql server using the sql_client class
        '''
        try:
            self.SQL.load_config()
            self.SQL.connect()
            self.SQL.check_tables()
            self.db_status = True
        except Exception:
            print(traceback.format_exc())
            self.db_status = False
            
        return
          
    def connections(self, host:str = "8.8.8.8", port: int = 53, timeout: int = 30):
        """        checks the connection to the internet as well as connection to the db, if the db connection fails
        it attempts to reconnect
        

        Args:
            host (str, optional): host to ping. Defaults to "8.8.8.8"(google-public-dns-a.google.com).
            port (int, optional): port to check on. Defaults to 53.
            timeout (int, optional): how long to wait. Defaults to 3.
        """
        self.network_status = False
        self.db_status = False
        try:
            # socket.setdefaulttimeout(3) #removed to allow desc through might lead to future errors need to find better solution
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            self.network_status = True
        except socket.error:
            print(traceback.format_exc())
            self.network_status = False
        try:
            self.db_status  = self.SQL.quit()
            self.SQL_startup()
        except Exception:
            print(traceback.format_exc())
            self.SQL_startup()
        
    def all_sockets_closed(self):
        """closes the server socket and displays the duration of the connection"""
        print("\n\nAll Clients Disconnected\nClosing The Server...")
        endtime: float = time.time()
        elapsed = time.strftime("%H:%M:%S", time.gmtime(endtime - self.starttime))
        unit = (
            "Seconds"
            if elapsed < "00:01:00"
            else "Minutes"
            if "01:00:00" > elapsed >= "00:01:00"
            else "Hours"
        )
        self.server_socket.close()
        print(f"\nThe Server Was Active For {elapsed} {unit}\n\n")
        
    def active_client_sockets(self):
        """prints the IP and PORT of all connected sockets"""
        print("\nCurrently Connected Sockets:")
        for c in self.connected_sockets:
            print("\t", c.getpeername())
        
        if self.gui_available: self.display.test_connections() #tests connections to gui
    
    def serve_client(self, current_socket : socket.socket):
        '''Takes the msg received from the client and handles it accordingly'''
        t: dt  = dt.now()
        try:               
            self.tool = self.config[current_socket.getpeername()[0]]
            self.logger.debug(f"serving client {current_socket.getpeername()[0]}")
        except KeyError:
            # client_data = "Tool not found" ### UNCOMMENT FOR DEPLOYMENT COMMENTED FOR DEBUGGING
            self.logger.error(f"{self.tool} not found please add to config")
        try:
            client_data:str = current_socket.recv(1024).decode()
            self.logger.debug(f"got message from {self.tool} at {t}")
            #client has 3 tries to send something
            zero_byte_count:int = 0
            while zero_byte_count < 3:
                if client_data:
                    break
                else:
                    zero_byte_count += 1
                    print(zero_byte_count)
                    raise ConnectionResetError
                    
            if zero_byte_count == int(3):
                current_socket.close()
           # self.bus_out.put(client_data)  # put the data in the bus for the main app to handle
          #  incoming = self.bus_in.get(timeout=5)  # wait for the main app to process the data
          #  print(incoming)
            date_time: str = time.strftime("%d/%m/%Y, %H:%M:%S")
            print(
                f"\nReceived new message form client {current_socket.getpeername()} at {date_time}:"
            )
            print(client_data)

        except ConnectionResetError or Exception:
            print(f"\nThe client {current_socket.getpeername()} has disconnected...")
            self.connected_sockets.remove(current_socket)
            current_socket.close()
            
            if len(self.connected_sockets) != 0:  # check for other connected sockets
                self.active_client_sockets()
            else:
                print("No more clients connected")
                self.active_client_sockets()
                
        except Exception:
            self.connected_sockets.remove(current_socket)
            current_socket.close()
            if len(self.connected_sockets) != 0:  # check for other connected sockets
                self.active_client_sockets()
            else:
                print("No more clients connected")
                self.active_client_sockets()
            print("serving client error")
            print(traceback.format_exc())
        else:
            # print(client_data)
            try:
                if (client_data == "Bye" or client_data.upper() == "QUIT" or client_data.upper() == "Q"):self.disconnect_socket(current_socket)
                elif client_data == "ID":self.get_id(current_socket)
                elif client_data == "META":sample_id = self.send_meta(current_socket, self.tool)
                elif client_data == "MEAS":self.meas_prot(current_socket, self.tool, t)
                elif client_data == "UPDATE":self.update(current_socket, self.tool)
                
                else:
                    self.tool = current_socket.getpeername()[0]
                    current_socket.send(client_data.encode())
            except ConnectionResetError:
                self.connected_sockets.remove(current_socket)
                
    def update(self, current_socket:socket.socket, tool:str):
        self.logger.debug(f"{tool} requested sample list")
        ids: list[str] = []
        if len(self.samples) != 0:
            for samp in self.samples:
                if not samp.insts[tool]:
                    ids.append(samp.id)
            msg: str = ",".join(ids)
        if len(ids) == 0:#if len(ids) == 0:
            print("No samples to update")
            msg:str = "None"
        self.logger.debug(f"current samples {msg} need measurent on {tool}")
        current_socket.send(msg.encode())

    def disconnect_socket(self, current_socket:socket.socket):
        self.logger.debug(f"Closing the socket with client {current_socket.getpeername()} now...")
        current_socket.send("Bye".encode())
        current_socket.recv(1024)
        self.logger.debug("removing client from active list and closing server side socket")
        self.connected_sockets.remove(current_socket)
        current_socket.close()
        self.logger.debug(" double checking active list")
                
        if len(self.connected_sockets) != 0:
            self.active_client_sockets()
        else:
            self.active_client_sockets()
    
    def send_meta(self, current_socket:socket.socket, tool:str):
        self.logger.debug(f"asking for sample id")
        
        current_socket.send("awaiting sampleid".encode())
        sample_id = current_socket.recv(1024).decode()
        
        self.logger.debug(f"sample {sample_id} is in {tool}")
        self.logger.debug(f"getting meta data for {sample_id}")
        
        self.logger.debug("asking position")
        
        current_socket.send("pos".encode())
        self.pos = current_socket.recv(1024).decode()
        
        self.logger.debug(f"got position {self.pos}")
        samp:sample = self.get_sample(tool, sample_id)
        self.logger.debug("sending description to client")
        
        current_socket.send(samp.description.encode())
        self.logger.debug(f"sent {samp.description} to client")
        
   
    def meas_prot(self, current_socket:socket.socket, tool:str, t:str):
        
        self.logger.debug(f"asking for sample id")
        current_socket.send("awaiting sampleid".encode())
        sample_id = current_socket.recv(1024).decode()
        self.logger.debug(f"{sample_id} is in {tool}")
        self.logger.debug("acquiring sample object")
        current_sample:sample = self.get_sample(tool, sample_id)
            
        values: list[list[str]]#list[list[str | dt] | list[str]] | list[list[str|float|int]]#list[list[str]] | list[str] 
        
        current_socket.send("send description please".encode())
        current_sample.description = current_socket.recv(1024).decode()
        
        
        self.logger.debug(f"recv {current_sample.description}")
        values = [
                    ["time", str(t)],
                    ["sample_id", sample_id],
                    ["Description", current_sample.description],
                    ["pos", self.pos]
                    ]
                              
        current_socket.send(f"awaiting value from {tool}".encode())
        value = current_socket.recv(32768).decode()
        print("GOT VALUE", value)
        current_socket.send("data received".encode())

        if tool == "fourpp":
            values.append(["resistance", value]) 
                    
            self.SQL.write(tool, values)
                
        if tool == "nearir":
            wvs: list[str]  = value.split(",")
            spec = current_socket.recv(32768).decode()
            time.sleep(1)
            spec = spec.split(",")
            current_socket.send("data received".encode())
            i: int = 0
            col: list[str] = []
            cols: list[str] = [] 
            for wv in wvs:
                wv2 = wv[:wv.index(".")]
                        # print(wv2)
                col = [f"{self.prefixes[tool]}_{wv2}", spec[i]]
                values.append(col)
                        
                cols.append(f"{wv2}")
                i += 1
                    #check if each wavelenght has a col
                    
            self.SQL.check_columns(tool, (",").join(cols))
                    
            self.SQL.write(tool, values)
                    
        if tool == "hall":
            data = value.split(",")
            print("DDATA", len(data), len(self.SQL.hall_cols))
            i = 0
            for sql_col in self.SQL.hall_cols:
                values.append([sql_col, data[i]])
                i += 1
                    
                    # value = float(value)
                    # values.append(["nb", str(value)])
                    
                    
            print(data)
            self.SQL.write(tool, values)
        
    def get_id(self, current_socket):
        try:
            print(current_socket.getpeername()[0])
            id: str = self.config[current_socket.getpeername()[0]]
        except KeyError:
            id = "Tool not found"
            self.logger.error(f"{self.tool} not found please add to config")
        current_socket.send(id.encode())
             #   print("Responded by: Sending the message back to the client")   
        
    def server(self):
        """server setup and socket handling"""
        print("Setting up server...")
        try:
            self.logger.debug(f"setting up server at {self.ADDR}")
            self.server_socket.bind(self.ADDR)  
        except OSError:
            traceback.print_exc()
        self.server_socket.listen()
        self.retries = 0
        print("\n* Server is ON *\n")
        print("Waiting for clients to establish connection...")
        self.starttime = time.time()
        self.connected_sockets = []  # list of the client sockets being connected
        while True:            
            try:       
                ready_to_read, _, _ = select.select( #
                    [self.server_socket] + self.connected_sockets, [], []
                )                
                if len(ready_to_read) != 0:
                    for current_socket in ready_to_read:
                        if (
                            current_socket is self.server_socket
                        ):  # if the current socket is the new socket we receive from the server
                            (client_socket, client_address) = current_socket.accept()
                            print("\nNew client joined!", client_address)
                            self.connected_sockets.append(client_socket)
                            self.active_client_sockets()
                            continue
                        self.serve_client(current_socket)
            
            except ValueError:
                while self.retries < 5:
                    self.server()
                    time.sleep(1)
                    self.retries += 1
                #all retries failed hard restarting server
                # traceback.print_exc()
                print(" VALUE ERROR")
                self.server_socket.close()
                
                self.server()
            except KeyboardInterrupt:
                self.all_sockets_closed()
                
            except Exception:
                print("Server issue")
                # print(traceback.format_exc())
                while self.retries < 5:
                    self.server()
                    time.sleep(1)
                    self.retries += 1
                #all retries failed hard restarting server
                
                self.server_socket.close()
                
                self.server()

    def quit(self):
        """
        closes tcp server then calls sql quit function
        """
        self.server_socket.close()
        self.SQL.quit()

class client():
    """
    A TCP client class for communicating with a main TCP server.
    This class provides methods to connect to a server, disconnect, and retrieve a client ID.
    It uses Python's socket and logging modules for network communication and logging.
    Attributes:
        ADDR (tuple): The (IP, port) address of the server.
        data (str): Placeholder for data received or sent.
        flag (int): Status flag for client state.
        tool (str): Identifier for the client, received from the server.
        soc (socket.socket): The socket object used for communication.
        logger (logging.Logger): Logger instance for this client.
    Methods:
        __init__(ip: str, port: int):
            Initializes the client with the server's IP and port, and sets up logging.
        connect():
            Connects to the server at the specified address. Logs connection status and errors.
        disconnect():
            Sends a disconnect message to the server and closes the socket.
        id():
            Requests and returns the client ID from the server. Caches the ID after the first request.
    """
    def __init__(self, ip:str , port:int):
        """_summary_ class for tool code to talk to main tcp server

        Args:
            ip (str): ip of server
            port (int):port of server
        """
        self.ADDR = (ip, port)
        
        self.data = ""
        self.flag = 0
        self.tool = ""
        
        self.soc: socket.socket
        #logging
        class_name = str(type(self))
        name = class_name.split(" ")[-1][:-1].replace("'", "")
        
        self.logger = logging.getLogger(name)
        
        self.logger.debug(f"tcp client starts with ip {ip} and port {port}")
        # self.msg_in = msg_in
        # self.msg_out = msg_out

    def connect(self):
        ''' connects to server
        '''
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.soc.connect(self.ADDR)
            self.logger.debug(f"connected to server at {self.ADDR}")
        except OSError or ConnectionRefusedError as e:
            self.logger.error(f"Connection to server at {self.ADDR} failed. Please check if the server is connected to the internet and that the IP and PORT numbers are correct on both ends")
            self.logger.error(traceback.format_exc())
            return e
            # sys.exit()
            
    def disconnect(self):
        '''
        disconnects
        '''
        self.logger.info(f"Disconnecting from server at {self.ADDR}")
        self.soc.send("Q".encode())
        self.soc.close()
            
    def id(self):
        '''
        gets id of client
        '''
        self.logger.debug("Requesting ID from server")
        if self.tool == "":
            self.soc.send("ID".encode())
            
            self.tool = self.soc.recv(1024).decode()
            self.logger.debug(f"Received ID from server: {self.tool}")
            # print(self.tool)
        else:
            return self.tool
        
class FileManager:
    """
    FileManager is a utility class for managing data files associated with a specific tool. It provides functionality to:
    - Initialize and manage a data directory for a given tool.
    - Enforce a maximum storage size limit for the data directory by deleting the oldest files when the limit is exceeded.
    - Write data to CSV files with specified headers and sample numbers, ensuring storage limits are respected.
    Attributes:
        tool (str): The name of the tool associated with the data files.
        path (str): The path to the data directory for the tool.
        size_lim (str): The maximum allowed size of the data directory in gigabytes.
        logger (logging.Logger): Logger instance for the class.
        
    Methods:
        __init__(tool: str, size_lim: str) -> None:
            Initializes the FileManager, sets up the data directory, and configures logging.
        rotating_file_handler() -> None:
            Checks the total size of the data directory and deletes the oldest file if the size exceeds the specified limit.
        write_data(sample_num: str, header: list[str], data: list[str] | list[list[str | float | int]]) -> None:
            Writes data to a CSV file in the data directory, using the provided sample number and header. Ensures storage limits are enforced before writing.
    """
    def __init__(self, tool: str, size_lim: str) -> None:
        """_summary_

        Args:
            tool (str): _description_
            size_lim (str): _description_
        """
        #logging
        class_name = str(type(self))
        name = class_name.split(" ")[-1][:-1].replace("'", "")
        
        self.logger = logging.getLogger(name)
        
        self.logger.debug(f"file manager starts with tool {tool} and size limit {size_lim} GB")
        
        self.tool = tool
        self.path: str = os.path.join(os.getcwd(),"tools", tool, "data")
        self.logger.debug(f"looking for data folder at {self.path}")
        if not os.path.exists(self.path):
            self.logger.debug(f"data folder not found at {self.path}, creating it")
            os.mkdir(self.path)    
        self.logger.debug(f"data folder found at {self.path}")
        
        self.size_lim = size_lim #in gb
    #first check folder size

    def rotating_file_handler(self) -> None:
        '''
        checks size of folder and compares it to size_lm if larger delete oldest file
        '''
        
        #get file size
        byte_lim: float = float(self.size_lim) * 1024 * 1024 * 1024
        total_size = 0
        self.logger.debug(f"checking folder size, limit is {byte_lim} bytes")
        for dirpath,_,filenames in os.walk(self.path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)                  
        
        
        if total_size > byte_lim:
            self.logger.debug(f"folder size {total_size} bytes is larger than limit {byte_lim} bytes, deleting oldest file")
            #sort files by date
            files = os.listdir(self.path)
            files.sort(key=lambda x: os.path.getmtime(os.path.join(self.path, x)))
            #delete oldest file
            oldest_file = os.path.join(self.path, files[0])
            self.logger.debug(f"deleting oldest file {oldest_file}")
            os.remove(oldest_file)
            # print(f"Deleted {oldest_file}")

    def write_data(self, sample_num: str, header: list[str], data: list[str] | list[list[str | float | int]]) -> None:
        """_summary_ writes data to data file

        Args:
            sample_num (str): sample number
            header (list[str]): column names
            data (list[str] | list[list[str  |  float  |  int]]): data to write out
        """
        
        self.logger.debug(f"writing data to file for sample {sample_num} with header {header} and data {data}")
        self.rotating_file_handler()
        self.date = dt.now().strftime("%m-%d-%Y, Hour %H Min %M Sec %S")
        
        file_name = f"{self.path}\\{sample_num}_{self.tool}_{self.date}.csv"
        self.logger.debug(f"writing data to file {file_name}")
        with open(file_name, "w") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(header)
            if isinstance(data[0], list):
                for row in data:
                    writer.writerow(row)
            else:
                writer.writerow(data)
        self.logger.debug(f"data written to file {file_name}")
#endregion
    



    
if __name__ == "__main__":
    sqltest = sql_client("config.json")
    sqltest.load_config()
    sqltest.connect()
    sqltest.check_tables()
    test_vals = [
        ["fpp_sample_id", "test_sample"],
        ["fpp_pos", "test_pos"],
        ["fpp_time", "test_time"],
        ["fpp_description", "test_description"],
        ["fpp_resistance", "test_resistance"]
        ]
    sqltest.write("fourpp", test_vals)