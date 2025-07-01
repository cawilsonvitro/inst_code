import pyodbc
import re
conn = pyodbc.connect(DRIVER='{ODBC Driver 17 for SQL Server}',
                      SERVER='10.40.0.114',
                      DATABASE = 'glass_test',
                      UID = "pylocal",
                      PWD = "pyvitro"
                    )
mycol = "\"2141\""
mytable = "test"
cursor = conn.cursor()


try:
    column_check = f"SELECT {mycol} FROM {mytable}"
    print(column_check)
    cursor.execute(column_check)
    my_result = cursor.fetchall()
        
except pyodbc.Error as e:
    print(e)
    cols_to_add = mycol.split(",")
    temp = ""
    i = 0
    for col_to_add in cols_to_add:
        cols_to_add[i] += " VARCHAR(255)"
        i += 1
    sql_col = ",".join(cols_to_add)
    sql = f"ALTER TABLE {mytable} ADD {sql_col}"
    cursor.execute(sql)
    cursor.commit()