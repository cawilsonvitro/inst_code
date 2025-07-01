import pyodbc
import json
import re

class sql_client():
    
    
    def __init__(self, config_path: str) -> None:
        #connction string
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
        #server connection
        self.sql: pyodbc.Connection
        self.cursor: pyodbc.Cursor
        #for building tables
        
        #sql querries
        self.tools:list[str] = []
        self.tables: list[str] = []
        self.missing_col_error:str = "207"
    
    
    def load_config(self):
        '''
        loads db connection config from config file
        '''
        with open('config.json', 'r') as file:
            config = json.load(file)
            self.config_db = config["Database_Config"]
            self.config_tools = config["Tool_ip"]
        #connection string from files
        self.host = self.config_db["host"]
        self.user = "pylocal"
        self.pw =  "pyvitro"
        self.driver = self.config_db["driver"]
        self.db = self.config_db["db"]
        #tool names from file
        self.tools = list(self.config_tools.values())
    
    
    def connect(self):
        #connectin to server
        self.sql = pyodbc.connect(
            host = self.host,
            user = self.user,
            driver = self.driver,
            password = self.pw
        )
        self.cursor = self.sql.cursor()
        
        # #checking for db then connecting
        
        self.cursor.execute("SELECT name FROM sys.databases;")
        
        self.dbs = [x[0] for x in self.cursor]
        if self.db not in self.dbs:
            self.cursor.execute(f"CREATE DATABASE {self.db}")
        
        self.sql.close()
        
        self.sql = pyodbc.connect(
            host = self.host,
            user = self.user,
            password = self.pw,
            driver = self.driver,
            database = self.db
        )

        self.cursor = self.sql.cursor()
        
        self.closed = self.sql.closed
    def get_col_name(self, error: str, positions: list[int]) -> str:
        '''Extracts the column name from the error message based on the position of the error code.
        Args:
            error (str): The error message string.
            pos (list[int]): A list containing the positions of the error code in the error message.
        Returns:
            str: The extracted column name.
        '''
        col_names: list[str] = []
        col_out: str = ""
        
        
        for pos in positions:
            
            p2 = len(error) - (pos + len(self.missing_col_error)) - 1
            
            
            
            rs = error[::-1][p2: ]
            
            rss = rs[rs.index('\'') + 1:]
            
            
            col_names.append(rss[:rss.index('\'')][::-1])
            
        col_out = ",".join(col_names)
        return col_out
    
    def check_columns(self, table: str , columns: str) -> None:
        
        try:
            print("FROM DB HANDLER")
            column_check: str = f"SELECT {columns} FROM {table}"
            print(column_check)
            self.cursor.execute(column_check)
            result = self.cursor.fetchall()
            
        except pyodbc.Error as e:
            print("I ran")
            error: str = str(e)
            positions = [match.start() for match in re.finditer(self.missing_col_error, error)]
            
            col_to_add: str = self.get_col_name(error, positions)
            print(f"adding {col_to_add}")
            sql = f"ALTER TABLE {table} ADD {col_to_add} VARCHAR(255)  DEFAULT 'CS'"
            
            self.cursor.execute(sql)
            self.sql.commit()
            print(f"Added columns {col_to_add} to table {table}")                                    

    
    
    def check_tables(self):
        temp: pyodbc.Cursor|None = None
        temp = self.cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
        self.tables = [x[2] for x in temp]
        for tool in self.tools:
            if tool not in self.tables:
                if tool == "fourpp":
                    self.cursor.execute(f"CREATE TABLE {tool} (time VARCHAR(255), resistance VARCHAR(255), sample_id VARCHAR(255))")
                if tool == "nearir":
                    self.cursor.execute(f"CREATE TABLE {tool} (time VARCHAR(255), sample_id VARCHAR(255))")
                if tool == "hall":
                    self.cursor.execute(f"CREATE TABLE {tool} (time VARCHAR(255), sample_id VARCHAR(255), nb VARCHAR(255))")
                if tool == "rdt":
                    self.cursor.execute(f"CREATE TABLE {tool} (time VARCHAR(255), sample_id VARCHAR(255), value VARCHAR(255))")
                    
        self.sql.commit()
    
    def write(self, table: str, values : list[list[str]]):
        self.cursor.execute("insert into fourpp(time, resistance) values ('dasgsa', 'dasgsa')")
        self.cursor.commit()
        #values is going to be formatted as 
        # values = [[col1, val1] , [col2, val2]]
        query = f"insert into {table}("
        end = "("
        for value in values:
            query += f"{value[0]}, " #building query 
            end += f"'{value[1]}', "
        end = end[:-2] + ")"
        
        query = query[:-2] + ")"
        
        query = query + " values " + end
        self.cursor.execute(query)
        self.sql.commit()
    
    
    def quit(self):
        #closes
        self.sql.close()
        

if __name__ == "__main__":
    
    
    values = [
        ["time","12:30"],
        ["resistance", "30"],
        ["sample_id", "123"]
    ]
    
    temp = sql_client('config.json')
    temp.load_config()
    temp.connect()
    temp.check_tables()
    temp.write("fourpp", values)
    cols = "1234,5678,9101112"
    temp.check_columns("test",cols)
    temp.quit()