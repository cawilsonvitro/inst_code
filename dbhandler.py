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
                # print(query)
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
                return False
        return True
    
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
                if self.check_for_illegals(value[0]):
                    query += f"{self.prefixes[table]}_{value[0]}, " #building query 
                else:
                    query += f"\"{self.prefixes[table]}_{value[0]}\", "
            else:
                if self.check_for_illegals(value[0]):
                    query += f"{value[0]}, " #building query 
                else:
                    query += f"\"{value[0]}\", "#building query 
                
            end += f"{value[1]}, "
        end = end[:-2] 
        
        query = query[:-2] 
        
        query = query + ")" + " values " + end + ")"
        self.cursor.execute(query)
        self.sql.commit()
    
    
    def quit(self):
        #closes
        self.sql.close()
        

if __name__ == "__main__":
    
    
    # values = [
    #     ["time","1"],
    #     ["resistance", "2"],
    #     ["sample_id", "3"]
    # ]
    #"insert into hall(ha_time, ha_sample_id, ha_DATE, ha_User_Name, ha_Sample_Name, ha_I(mA), ha_B, ha_D, ha_D_T, ha_MN, ha_T(K), ha_Nb, ha_u, ha_rho, ha_RH, ha_RHA, ha_RHB, ha_NS, ha_SIGMA, ha_DELTA, ha_ALPHA, ha_Vab+I, ha_Vbc+I, ha_Vac+I, ha_Vmac+I, ha_V-mac+I, ha_Vcd+I, ha_Vda+I, ha_Vbd+I, ha_Vmbd+I, ha_V-mbd, ha_Vab-I, ha_Vbc-I, ha_Vac-I, ha_Vmac-I, ha_V-mac-I, ha_Vcd-I, ha_Vda-I, ha_Vbd-I, ha_Vmbd-I, ha_Rs) values ('07-03-2025, Hour 13 Min 04 Sec 35', '123', '07-09-2024', 'KF', 'C-15289A', '7.000', '0.550', '0.120', '0.100', '300', '300', '-1.875E+21', '1.312E+01', '2.537E-04', '-3.329E-03', '-3.326E-03', '-3.331E-03', '-2.250E+16', '3.942E+03', '1.526E-02', '7.346E-01', '-27.892', '-37.964', '10.080', '9.970', '10.185', '-27.895', '-37.973', '10.080', '10.188', '9.977', '27.878', '37.956', '-10.091', '-9.985', '-10.196', '27.875', '37.951', '-10.090', '-10.197', '-9.981')"
    temp = sql_client('config.json')
    temp.load_config()
    temp.connect()
    # temp.check_tables()
    
    
    
    
    
    
    
    
    
    
    
    
    
    #'insert into hall("ha_time", " ha_sample_id", " ha_DATE", " ha_User_Name", " ha_Sample_Name", " ha_I(mA)", " ha_B", " ha_D", " ha_D_T", " ha_MN", " ha_T(K)", " ha_Nb", " ha_u", " ha_rho", " ha_RH", " ha_RHA", " ha_RHB", " ha_NS", " ha_SIGMA", " ha_DELTA", " ha_ALPHA", " ha_Vab+I", " ha_Vbc+I", " ha_Vac+I", " ha_Vmac+I", " ha_V-mac+I", " ha_Vcd+I", " ha_Vda+I", " ha_Vbd+I", " ha_Vmbd+I", " ha_V-mbd", " ha_Vab-I", " ha_Vbc-I", " ha_Vac-I", " ha_Vmac-I", " ha_V-mac-I", " ha_Vcd-I", " ha_Vda-I", " ha_Vbd-I", " ha_Vmbd-I", " ha_Rs") 
    # values ("07-03-2025", " Hour 13 Min 04 Sec 35", " 123", " 07-09-2024", " KF", " C-15289A", " 7.000", " 0.550", " 0.120", " 0.100", " 300", " 300", " -1.875E+21", " 1.312E+01", " 2.537E-04", " -3.329E-03", " -3.326E-03", " -3.331E-03", " -2.250E+16", " 3.942E+03", " 1.526E-02", " 7.346E-01", " -27.892", " -37.964", " 10.080", " 9.970", " 10.185", " -27.895", " -37.973", " 10.080", " 10.188", " 9.977", " 27.878", " 37.956", " -10.091", " -9.985", " -10.196", " 27.875", " 37.951", " -10.090", " -10.197")'
    
    temp.sql.execute("INSERT INTO hall (ha_time, ha_sample_id, \"ha_I(mA)\") VALUES (\"07-03-2025, Hour 13 Min 04 Sec 35\",2,3)")
    temp.sql.commit()
    
    cols = "ha_time, ha_sample_id, ha_DATE, ha_User_Name, ha_Sample_Name, ha_I(mA), ha_B, ha_D, ha_D_T, ha_MN, ha_T(K), ha_Nb, ha_u, ha_rho, ha_RH, ha_RHA, ha_RHB, ha_NS, ha_SIGMA, ha_DELTA, ha_ALPHA, ha_Vab+I, ha_Vbc+I, ha_Vac+I, ha_Vmac+I, ha_V-mac+I, ha_Vcd+I, ha_Vda+I, ha_Vbd+I, ha_Vmbd+I, ha_V-mbd, ha_Vab-I, ha_Vbc-I, ha_Vac-I, ha_Vmac-I, ha_V-mac-I, ha_Vcd-I, ha_Vda-I, ha_Vbd-I, ha_Vmbd-I, ha_Rs".split(",")
    values = "07-03-2025, Hour 13 Min 04 Sec 35, 123, 07-09-2024, KF, C-15289A, 7.000, 0.550, 0.120, 0.100, 300, 300, -1.875E+21, 1.312E+01, 2.537E-04, -3.329E-03, -3.326E-03, -3.331E-03, -2.250E+16, 3.942E+03, 1.526E-02, 7.346E-01, -27.892, -37.964, 10.080, 9.970, 10.185, -27.895, -37.973, 10.080, 10.188, 9.977, 27.878, 37.956, -10.091, -9.985, -10.196, 27.875, 37.951, -10.090, -10.197, -9.981".split(",")
    a = []
    b = []
    i = 0
    for col in cols:
        a.append([col,values[i]])
        i += 1
    
    temp.write("hall", a)
    
    # temp.sql.cursor()
    # temp.sql.execute("insert into hall() values ('07-03-2025, Hour 13 Min 04 Sec 35', '123', '07-09-2024', 'KF', 'C-15289A', '7.000', '0.550', '0.120', '0.100', '300', '300', '-1.875E+21', '1.312E+01', '2.537E-04', '-3.329E-03', '-3.326E-03', '-3.331E-03', '-2.250E+16', '3.942E+03', '1.526E-02', '7.346E-01', '-27.892', '-37.964', '10.080', '9.970', '10.185', '-27.895', '-37.973', '10.080', '10.188', '9.977', '27.878', '37.956', '-10.091', '-9.985', '-10.196', '27.875', '37.951', '-10.090', '-10.197', '-9.981')")
    # temp.sql.commit()
    # temp.write("fourpp", values)
    # cols = "70.23523,60.1241,1051.8,1054.4367376025,1057.07438441,1059.7129404225,1062.35240564,1064.9927800625,1067.63406369,1070.2762565225,1072.9193585599999,1075.5633698025,1078.20829025,1080.8541199024999,1083.50085876,1086.1485068225,1088.79706409,1091.4465305625,1094.09690624,1096.7481911225,1099.40038521,1102.0534885025,1104.7075009999999,1107.3624227025,1110.0182536099999,1112.6749937225,1115.33264304,1117.9912015625,1120.65066929,1123.3110462225,1125.9723323599999,1128.6345277025,1131.2976322499999,1133.9616460025,1136.62656896,1139.2924011225,1141.95914249,1144.6267930625,1147.2953528399999,1149.9648218225,1152.63520001,1155.3064874025,1157.978684,1160.6517898025,1163.32580481,1166.0007290224999,1168.67656244,1171.3533050624999,1174.03095689,1176.7095179225,1179.38898816,1182.0693676025,1184.75065625,1187.4328541025,1190.1159611599999,1192.7999774225,1195.48490289,1198.1707375624999,1200.85748144,1203.5451345225,1206.2336968099999,1208.9231683025,1211.613549,1214.3048389025,1216.9970380099999,1219.6901463225,1222.38416384,1225.0790905625,1227.7749264899999,1230.4716716225,1233.16932596,1235.8678895025,1238.5673622499999,1241.2677442025,1243.96903536,1246.6712357225,1249.37434529,1252.0783640625,1254.78329204,1257.4891292225,1260.19587561,1262.9035312024998,1265.612096,1268.3215700025,1271.03195321,1273.7432456225,1276.45544724,1279.1685580624999,1281.88257809,1284.5975073225,1287.31334576,1290.0300934025,1292.74775025,1295.4663163025,1298.1857915599999,1300.9061760225,1303.62746969,1306.3496725625,1309.07278464,1311.7968059225,1314.52173641,1317.2475761025,1319.974325,1322.7019831025,1325.43055041,1328.1600269225,1330.89041264,1333.6217075625,1336.35391169,1339.0870250225,1341.82104756,1344.5559793025,1347.29182025,1350.0285704025,1352.76622976,1355.5047983225,1358.2442760899999,1360.9846630625,1363.72595924,1366.4681646225,1369.21127921,1371.9553030025,1374.700236,1377.4460782024998,1380.19282961,1382.9404902224999,1385.68906004,1388.4385390625,1391.18892729,1393.9402247225,1396.69243136,1399.4455472025,1402.19957225,1404.9545065025,1407.71034996,1410.4671026225,1413.2247644899999,1415.9833355625,1418.74281584,1421.5032053225,1424.2645040099999,1427.0267119025,1429.789829,1432.5538553024999,1435.3187908099999,1438.0846355224999,1440.8513894399998,1443.6190525625,1446.38762489,1449.1571064225,1451.92749716,1454.6987971025,1457.4710062499998,1460.2441246025,1463.01815216,1465.7930889225,1468.56893489,1471.3456900625,1474.12335444,1476.9019280225,1479.68141081,1482.4618028025,1485.2431040000001,1488.0253144025,1490.80843401,1493.5924628225,1496.37740084,1499.1632480624999,1501.95000449,1504.7376701225,1507.52624496,1510.3157290025,1513.10612225,1515.8974247024998,1518.68963636,1521.4827572225,1524.27678729,1527.0717265624999,1529.86757504,1532.6643327225,1535.46199961,1538.2605757024999,1541.0600610000001,1543.8604555025,1546.66175921,1549.4639721224999,1552.26709424,1555.0711255625,1557.87606609,1560.6819158225,1563.4886747599999,1566.2963429024999,1569.1049202499999,1571.9144068024998,1574.72480256,1577.5361075225,1580.34832169,1583.1614450625,1585.97547764,1588.7904194225,1591.60627041,1594.4230306025,1597.2407,1600.0592786025,1602.87876641,1605.6991634225,1608.52046964,1611.3426850625,1614.16580969,1616.9898435225,1619.81478656,1622.6406388025,1625.46740025,1628.2950709025,1631.1236507600001,1633.9531398225,1636.78353809,1639.6148455624998,1642.44706224,1645.2801881225,1648.11422321,1650.9491675025001,1653.785021,1656.6217837025001,1659.45945561,1662.2980367225,1665.13752704,1667.9779265625,1670.81923529,1673.6614532224999,1676.50458036,1679.3486167024998,1682.19356225,1685.0394170025002,1687.8861809599998,1690.7338541225,1693.58243649,1696.4319280625,1699.28232884,1702.1336388225,1704.98585801,1707.8389864024998,1710.6930240000002,1713.5479708025,1716.4038268099998,1719.2605920225,1722.1182664399998,1724.9768500625,1727.83634289,1730.6967449224999,1733.55805616,1736.4202766025,1739.28340625,1742.1474451025001,1745.01239316,1747.8782504225,1750.74501689,1753.6126925625,1756.48127744,1759.3507715225,1762.2211748099999,1765.0924873025,1767.9647089999999,1770.8378399025,1773.71188001,1776.5868293224999,1779.46268784,1782.3394555625,1785.21713249,1788.0957186225,1790.97521396,1793.8556185025,1796.7369322499999,1799.6191552025,1802.50228736,1805.3863287225,1808.27127929,1811.1571390625,1814.04390804,1816.9315862224998,1819.82017361,1822.7096702025,1825.6000760000002,1828.4913910025,1831.38361521,1834.2767486225,1837.17079124,1840.0657430625001,1842.96160409,1845.8583743225,1848.75605376,1851.6546424025,1854.55414025,1857.4545473025,1860.35586356,1863.2580890225,1866.16122369,1869.0652675625,1871.97022064,1874.8760829225,1877.78285441,1880.6905351025,1883.599125,1886.5086241025,1889.41903241,1892.3303499224999,1895.2425766400002,1898.1557125625,1901.0697576900002,1903.9847120225,1906.90057556,1909.8173483024998,1912.73503025,1915.6536214025,1918.57312176,1921.4935313225,1924.41485009,1927.3370780625,1930.26021524,1933.1842616225,1936.10921721,1939.0350820025,1941.961856,1944.8895392025,1947.81813161,1950.7476332225,1953.67804404,1956.6093640625,1959.54159329,1962.4747317225,1965.40877936,1968.3437362025002,1971.27960225,1974.2163775025,1977.15406196,1980.0926556225,1983.03215849,1985.9725705625,1988.91389184,1991.8561223225001,1994.79926201,1997.7433109025,2000.688269,2003.6341363024999,2006.58091281,2009.5285985225,2012.47719344,2015.4266975625,2018.37711089,2021.3284334225,2024.28066516,2027.2338061025,2030.18785625,2033.1428156025,2036.09868416,2039.0554619225,2042.0131488900001,2044.9717450625,2047.93125044,2050.8916650225,2053.85298881,2056.8152218024998,2059.778364,2062.7424154025002,2065.70737601,2068.6732458225,2071.64002484,2074.6077130625,2077.5763104899997,2080.5458171225,2083.51623296,2086.4875580025,2089.4597922499997,2092.4329357025,2095.40698836,2098.3819502224997,2101.35782129,2104.3346015625,2107.3122910399998,2110.2908897224997,2113.27039761,2116.2508147025,2119.232141,2122.2143765025003,2125.1975212099996,2128.1815751225004,2131.1665382399997,2134.1524105625003,2137.13919209,2140.1268828225,2143.1154827600003,2146.1049919025,2149.09541025,2152.0867378025,2155.0789745600005,2158.0721205225,2161.06617569,2164.0611400625003,2167.05701364,2170.0537964225,2173.0514884100003,2176.0500896025,2179.0496000000003,2182.0500196025,2185.05134841,2188.0535864225003,2191.05673364,2194.0607900625,2197.06575569,2200.0716305224996,2203.07841456,2206.0861078025,2209.0947102500004,2212.1042219025003,2215.1146427599997,2218.1259728225,2221.13821209,2224.1513605625,2227.16541824,2230.1803851225,2233.19626121,2236.2130465025,2239.2307410000003,2242.2493447025,2245.26885761,2248.2892797225,2251.3106110400004,2254.3328515625,2257.3560012899998,2260.3800602225,2263.40502836,2266.4309057025002,2269.45769225,2272.4853880025003,2275.51399296,2278.5435071225,2281.57393049,2284.6052630625,2287.63750484,2290.6706558225,2293.70471601,2296.7396854025,2299.775564,2302.8123518025,2305.85004881,2308.8886550225,2311.92817044,2314.9685950625,2318.00992889,2321.0521719225,2324.09532416,2327.1393856024997,2330.18435625,2333.2302361025,2336.27702516,2339.3247234225,2342.37333089,2345.4228475625,2348.47327344,2351.5246085225,2354.5768528099998,2357.6300063025,2360.684069,2363.7390409025,2366.79492201,2369.8517123225,2372.90941184,2375.9680205625,2379.02753849,2382.0879656225,2385.1493019600002,2388.2115475025003,2391.27470225,2394.3387662024998,2397.40373936,2400.4696217225,2403.53641329,2406.6041140625002,2409.67272404,2412.7422432225,2415.81267161,2418.8840092025002,2421.9562560000004,2425.0294120025,2428.10347721,2431.1784516225,2434.25433524,2437.3311280625003,2440.4088300900003,2443.4874413224998,2446.5669617599997,2449.6473914025,2452.72873025,2455.8109783025,2458.89413556,2461.9782020225,2465.06317769,2468.1490625625,2471.23585664,2474.3235599225,2477.41217241,2480.5016941025,2483.592125,2486.6834651025,2489.77571441,2492.8688729225,2495.96294064,2499.0579175625,2502.15380369,2505.2505990225,2508.34830356,2511.4469173025,2514.54644025,2517.6468724025"
    # datas = "1,2,3,4,5,6"
    # i = 0
    
    #'ALTER TABLE test ADD t_70 VARCHAR(255),t_ 60 VARCHAR(255)'
    #'ALTER TABLE hall ADD "ha_DATE" VARCHAR(255),"ha_User_Name" VARCHAR(255),"ha_Sample_Name" VARCHAR(255),"ha_DATE" VARCHAR(255),"ha_User_Name" VARCHAR(255),"ha_Sample_Name" VARCHAR(255),"ha_I(mA)" VARCHAR(255),"ha_B" VARCHAR(255),"ha_D" VARCHAR(255),"ha_D_T" VARCHAR(255),"ha_MN" VARCHAR(255),"ha_T(K)" VARCHAR(255),"ha_Nb" VARCHAR(255),"ha_u" VARCHAR(255),"ha_rho" VARCHAR(255),"ha_RH" VARCHAR(255),"ha_RHA" VARCHAR(255),"ha_RHB" VARCHAR(255),"ha_NS" VARCHAR(255),"ha_SIGMA" VARCHAR(255),"ha_DELTA" VARCHAR(255),"ha_ALPHA" VARCHAR(255),"ha_Vab+I:" VARCHAR(255),"ha_Vbc+I:" VARCHAR(255),"ha_Vac+I:" VARCHAR(255),"ha_Vmac+I:" VARCHAR(255),"ha_V-mac+I:" VARCHAR(255),"ha_Vcd+I:" VARCHAR(255),"ha_Vda+I:" VARCHAR(255),"ha_Vbd+I:" VARCHAR(255),"ha_Vmbd+I:" VARCHAR(255),"ha_V-mbd+I:" VARCHAR(255),"ha_Vab-I:" VARCHAR(255),"ha_Vbc-I:" VARCHAR(255),"ha_Vac-I:" VARCHAR(255),"ha_Vmac-I:" VARCHAR(255),"ha_V-mac-I:" VARCHAR(255),"ha_Vcd-I:" VARCHAR(255),"ha_Vda-I:" VARCHAR(255),"ha_Vbd-I:" VARCHAR(255),"ha_Vmbd-I:" VARCHAR(255),"ha_V-mbd-I:" VARCHAR(255),"ha_Rs" VARCHAR(255)'    
    # temp.sql.cursor()
    # temp.sql.execute('ALTER TABLE hall ADD ha_DATE VARCHAR(255), ha_User_Name VARCHAR(255)')
    
    # batches = []
    # batch = []
    
    
    # a = cols.split(",")
    # for col in a:
    #     end = col.index(".")
    #     a[i] = f"{col[:end]}"
    #     i+=1
    # cols = (",").join(a)
    # print(cols)
    # temp.check_columns("test",cols)
    
    
    
    # tempstwo = []
    # temptwo = []
    # ds = datas.split(",")
    # cs = cols.split(",")
    
    # i = 0
    # for d in ds:
    #     temptwo = [cs[i], d]     
    #     tempstwo.append(temptwo)
        
    #     i += 1
    # temp.write("test", tempstwo)
    
    
    temp.quit()