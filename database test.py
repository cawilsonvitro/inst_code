# # using https://stackoverflow.com/questions/33725862/connecting-to-microsoft-sql-server-using-python for pydb
# # using https://www.w3schools.com/python/python_mysql_getstarted.asp for mysql
# # using https://www.geeksforgeeks.org/sql-using-python/ for sqlite3
# #connection string Server=localhost;Database=master;Trusted_Connection=True;

# #Server=localhost;Database=master;Trusted_Connection=True;
# #C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\Binn\Templates


#for microsoft
#https://learn.microsoft.com/en-us/sql/connect/python/python-driver-for-sql-server?view=sql-server-ver17

#using pyodbc


# connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'


# SERVER = 'localhost'
# DATABASE = 'master'
# USERNAME = 'VITRO\\C376038'
# PASSWORD = '#Shadow1757'
# connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Encrypt = no' 
# conn = pyodbc.connect(connectionString)
# conn.close()


# # using https://www.w3schools.com/python/python_mysql_getstarted.asp for mysql pw: 1234 usr test pw same

# import mysql.connector

# mydb = mysql.connector.connect(
#   host="localhost",
#   user="root",
#   password="1234",
#   database = "mydatabase"
# )

# print(mydb)

# mycursor = mydb.cursor()

# mycursor.execute("SHOW DATABASES")

# xs = [x[0] for x in mycursor]

# if "mydatabase" not in xs: mycursor.execute("CREATE DATABASE mydatabase")

# # creating table 

# mycursor = mydb.cursor()

# mycursor.execute("CREATE TABLE customers (name VARCHAR(255), address VARCHAR(255))")


# #checking  if table exists
# mycursor = mydb.cursor()

# mycursor.execute("SHOW TABLES")
# xs = [x[0] for x in mycursor]
# if "customers" not in xs: mycursor.execute("CREATE TABLE customers (name VARCHAR(255), address VARCHAR(255))")

# # adding column
# # mycursor.execute("ALTER TABLE customers ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY")

# #adding data
# sql = "INSERT INTO customers (name, address) VALUES (%s, %s)"
# val = ("John", "Highway 21")
# mycursor.execute(sql, val)

# mydb.commit()

# print(mycursor.rowcount, "record inserted.")



#for sql using google ai
import pyodbc
import re
conn = pyodbc.connect(DRIVER='{ODBC Driver 17 for SQL Server}',
                      SERVER='10.40.0.114',
                      DATABASE = 'glass_test',
                      UID = "pylocal",
                      PWD = "pyvitro"
                      )

missing_col_error ="207"
try:
    cursor = conn.cursor()
    mycol = "test, test2"
    mytable = "fourpp"
    column_check = f"SELECT {mycol} FROM {mytable}"
    cursor.execute(column_check)

    my_reuslt = cursor.fetchall()

    # print(my_reuslt)
    
except pyodbc.Error as e:
    # print("Error:", e) #Error: ('42S22', "[42S22] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Invalid column name 'test'. (207) (SQLExecDirectW); [42S22] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Invalid column name 'test2'. (207)")
    error = str(e)
    position = [match.start() for match in re.finditer(missing_col_error, error)]
    
    # print(position)
    # print(position)
    
def reverse_search(str: str):
    pass


# a = [0,1,2,3]
# b = a[::-1]
# c = b[::-1]
# print(c)
    
t = r"('42S22', \"[42S22] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Invalid column name 'test'. (207) (SQLExecDirectW); [42S22] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Invalid column name 'test2'. (207)\")"
rt = t[::-1] #)"\)702( .'2tset' eman nmuloc dilavnI]revreS LQS[]revreS LQS rof 71 revirD CBDO[]tfosorciM[ ]22S24[ ;)WtceriDcexELQS( )702( .'tset' eman nmuloc dilavnI]revreS LQS[]revreS LQS rof 71 revirD CBDO[]tfosorciM[ ]22S24["\ ,'22S24'(
# print(rt)
# print(len(t)-rt.index("4") - 1)
# print(t.rindex("4"))

# print(t.index("7"))
# print(len(t) - rt.rindex("7") - 1)
    


pos1 = position[0]
# print(pos1)
# print(t[pos1 + 1 : pos1 + 1 + len(missing_col_error)])

p1 = len(t) - (pos1) - 1
p2 = len(t) - (pos1 + len(missing_col_error)) - 1

# print(p1,p2)
# print(rt[p2:p1 + 10])

rs = rt[p2:]

rssp1 = rs.index('\'')

# print(rs[rssp1 + 1:])
rs = rs[rssp1 + 1:]
s = rs[:rs.index('\'')][::-1]
# print(s)



def get_col_name(error: str, positions: list[int]) -> str:
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
        
        p1 = len(error) - pos - 1
        p2 = len(error) - (pos + len(missing_col_error)) - 1
        
        
        
        rs = error[::-1][p2: ]
        
        rss = rs[rs.index('\'') + 1:]
        
        
        col_names.append(rss[:rss.index('\'')][::-1])
        
    col_out = ",".join(col_names)
    return col_out
    
tpos = [102, 217]
    
print(get_col_name(t,tpos))

# pos2 = position[1]
# print(pos2)
# print(t[pos2 + 1 : pos2 + 1 + len(missing_col_error)])

# p3 = len(t) - (pos2) - 1
# p4 = len(t) - (pos2 + len(missing_col_error)) - 1

# print(p3,p4)
# print(rt[p4:p3 + 10][::-1])















# SELECT CASE SERVERPROPERTY('IsIntegratedSecurityOnly')
# WHEN 1 THEN 'Windows Authentication'
# WHEN 0 THEN 'Windows and SQL Server Authentication'
# END as [Authentication Mode]
#python user: pylocal pw: pyvitro


#ip of server
#10.40.0.114 1433 wifi
#192.168.1.1 1433 local
#127.0.0.1 1433
#