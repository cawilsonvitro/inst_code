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
conn = pyodbc.connect(DRIVER='{ODBC Driver 17 for SQL Server}',
                      SERVER='localhost',
                      DATABASE = 'glass_test',
                      UID = "pylocal",
                      PWD = "pyvitro"
                      )

cursor = conn.cursor()

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