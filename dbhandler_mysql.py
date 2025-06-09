import mysql
import mysql.connector
import json


#for typing
from typing import Union, Any
import mysql.connector.cursor_cext

mysql.connector.connection_cext.CMySQLConnection
mysql.connector.cursor_cext.CMySQLCursor
class sql_client():
  
  
    def __init__(self, config_path: str):
        #connction string
        self.host: str = ""
        self.user: str = ""
        self.pw: str = ""
        self.db: str = ""
        
        #config 
        self.config_path:str = config_path
        self.config_db:dict = {
            
            }
        self.config_tools:dict = {
            
        }
        #server connection
        self.sql: mysql.connector.connection_cext.CMySQLConnection|None = None
        self.cursor: mysql.connector.cursor_cext.CMySQLCursor|None
        #for building tables
        
        #sql querries
        self.tools:list[str] = []
        self.tables: list[str] = []
        
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
        self.user = self.config_db["user"]
        self.pw = self.config_db["pw"]
        self.db = self.config_db["db"]
        #tool names from file
        self.tools = list(self.config_tools.values())
        
        
            
        
    
    def connect(self):
        #connectin to server
        self.sql = mysql.connector.connect(
            host = self.host,
            user = self.user,
            password = self.pw,
        )
        self.cursor = self.sql.cursor()
        
        #checking for db then connecting
        
        self.cursor.execute("SHOW DATABASES")
        
        self.dbs = [x[0] for x in self.cursor]
        
        if self.db not in self.dbs:
            self.cursor.execute(f"CREATE DATABASE {self.db}")
        
        self.sql.close()
        
        self.sql = mysql.connector.connect(
            host = self.host,
            user = self.user,
            password = self.pw,
            database = self.db
        )

        self.cursor = self.sql.cursor()
        
        self.connection = self.sql.is_connected()
        
    def check_tables(self):
        self.cursor.execute("SHOW TABLES")
        self.tables = [x[0] for x in self.cursor]
        
        for tool in self.tools:
            if tool not in self.tables:
                if tool == "fourpp":
                    self.cursor.execute(f"CREATE TABLE {tool} (time VARCHAR(255), resistance VARCHAR(255))")
    
    
    def write(self, table, values):
        #values is going to be formatted as 
        # values = [[col1, val1] , [col2, val2]]
        query = f"INSERT INTO {table} ("
        end = "("
        inputs = []
        for value in values:
            query += f"{value[0]}, " #building query 
            inputs.append(value[1])
            end += "%s, "
        end = end[:-2] + ")"
        
        query = query[:-2] + ")"
        
        query = query + " VALUES " + end
        print(query)
        self.cursor.execute(query,inputs)
        self.sql.commit()
        
    def quit(self):
        self.sql.close()
        
if __name__ == "__main__":
    temp = sql_client("config.json")
    temp.load_config()
    temp.connect()
    temp.sql.is_connected()
    temp.check_tables()
    
    
    
    values = [
        ["time","12:30"],
        ["resistance", "30"]
    ]
    
    temp.write("fourpp", values)
    
    
    