import pyodbc
import json
import re
import time
from hall_parser import parse

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
        self.illegal_char: list[str] = ["+","(",")","-"]
        self.illegal_val: list[str] = ["hour", "second", "minute", "min"]
        self.hall_cols: list[str] = []
        #int prefixes
        self.prefixes: dict[str,str] = {
            
        }

    
    def load_config(self):
        '''
        loads db connection config from config file
        '''
        with open('config.json', 'r') as file:
            config = json.load(file)
            self.config_db = config["Database_Config"]
            self.config_tools = config["Tool_ip"]
            self.prefixes = config["Tool_pre"]
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
        
    def check_columns(self, table: str , columns: str) -> None:
        
        try:
            print("FROM DB HANDLER")
            # print(columns)
            column_check: str = f"SELECT "#\"{columns}\" FROM {table}"
            temp_list = columns.split(",")
            for column in temp_list:
                column_check += f"\"{self.prefixes[table]}_{column}\", "
            column_check = column_check[:-2] + f" FROM {table}"
                
            self.cursor.execute(column_check)
            result = self.cursor.fetchall()
            
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
   
                print(f"adding {cols_to_add}")
                #  \"{col_to_add}\" VARCHAR(255)"
                print(query)
                self.cursor.execute(query)
                self.sql.commit()
                   
    def check_tables(self):
        temp: pyodbc.Cursor|None = None
        temp = self.cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
        self.tables = [x[2] for x in temp]
        hall_name:str = ""
        for tool in self.tools:
            if tool == "hall":hall_name = tool
            if tool not in self.tables:
                if tool == "fourpp":
                    self.cursor.execute(f"CREATE TABLE {tool} ({self.prefixes[tool]}_time VARCHAR(255), {self.prefixes[tool]}_resistance VARCHAR(255), {self.prefixes[tool]}_sample_id VARCHAR(255))")
                if tool == "nearir":
                    self.cursor.execute(f"CREATE TABLE {tool} ({self.prefixes[tool]}_time VARCHAR(255), {self.prefixes[tool]}_sample_id VARCHAR(255))")
                if tool == "hall":
                    self.cursor.execute(f"CREATE TABLE {tool} ({self.prefixes[tool]}_time VARCHAR(255), {self.prefixes[tool]}_sample_id VARCHAR(255))")
                if tool == "rdt":
                    self.cursor.execute(f"CREATE TABLE {tool} ({self.prefixes[tool]}_time VARCHAR(255), {self.prefixes[tool]}_sample_id VARCHAR(255), {self.prefixes[tool]}_value VARCHAR(255))")
                if tool == "test":
                    self.cursor.execute(f"CREATE TABLE {tool} (t_time VARCHAR(255), t_sample_id VARCHAR(255))")
        self.sql.commit()
        
        time.sleep(1) #wait for sql changes to come in
        temp = self.cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
        self.tables = [x[2] for x in temp]
        headers:list[str] = []
        datas:list[str]  = []
        self.hall_cols, datas = parse(r"tools\hall\data\sample_file.txt")
        self.check_columns(hall_name, (",").join(self.hall_cols))                    
        
        
    def check_for_illegals(self, col_name: str) -> bool:
        '''
        checks for sql banned chars in col name
        inputs:
        col_name: name you want to check
        '''
        for char in self.illegal_char:
            if col_name.find(char) != -1:
                return True
        return False
    
    def check_for_keywords(self, value: str) ->bool:
        
        for word in self.illegal_val:
            if word.lower() in value.lower():
                return False
            return True
    
    def write(self, table: str, values : list[list[str]]):
        # self.cursor.execute("insert into fourpp(fpp_time, fpp_sample_id, fpp_resistance) values ('12:30', '30', '123')")
        # self.cursor.commit()
        #values is going to be formatted as         
        # values = [[col1, val1] , [col2, val2]]
        
        query = f"insert into {table}("
        end = "("
        for value in values:
            if self.prefixes[table] not in value[0]:
                if not self.check_for_illegals(value[0]):
                    query += f"{self.prefixes[table]}_{value[0]}," #building query 
                else:
                    query += f"\"{self.prefixes[table]}_{value[0]}\","
            else:
                if not self.check_for_illegals(value[0]):
                    query += f"{value[0]}," #building query 
                else:
                    query += f"\"{value[0]}\","
                
            end += f"'{value[1]}', "
        end = end[:-2] 
        
        query = query[:-1] 
        
        query = query + ")" + " values " + end + ")"
        print(query)
        self.cursor.execute(query)
        self.sql.commit()
    
    
    def quit(self):
        #closes
        self.sql.close()
        

if __name__ == "__main__":
    
    
   
    temp = sql_client('config.json')
    temp.load_config()
    temp.connect()
    # temp.check_tables()
    
    # insert into hall
    # (ha_time,ha_sample_id,ha_DATE,ha_User_Name,ha_Sample_Name,\"ha_I(mA)\"",ha_B,ha_D,ha_D_T,ha_MN,ha_T(K),ha_Nb,ha_u,ha_rho,ha_RH,ha_RHA,ha_RHB,ha_NS,ha_SIGMA,ha_DELTA,ha_ALPHA,ha_Vab+I,ha_Vbc+I,ha_Vac+I,ha_Vmac+I,ha_V-mac+I,ha_Vcd+I,ha_Vda+I,ha_Vbd+I,ha_Vmbd+I,ha_V-mbd,ha_Vab-I,ha_Vbc-I,ha_Vac-I,ha_Vmac-I,ha_V-mac-I,ha_Vcd-I,ha_Vda-I,ha_Vbd-I,ha_Vmbd-I,ha_Rs) values ('07-07-2025, Hour 09 Min 50 Sec 22', '123', '07-09-2024', 'KF', 'C-15289A', '7.000', '0.550', '0.120', '0.100', '300', '300', '-1.875E+21', '1.312E+01', '2.537E-04', '-3.329E-03', '-3.326E-03', '-3.331E-03', '-2.250E+16', '3.942E+03', '1.526E-02', '7.346E-01', '-27.892', '-37.964', '10.080', '9.970', '10.185', '-27.895', '-37.973', '10.080', '10.188', '9.977', '27.878', '37.956', '-10.091', '-9.985', '-10.196', '27.875', '37.951', '-10.090', '-10.197', '-9.981')
    
    
    
    
    
    
    
    
    
    
    
    
    temp.quit()