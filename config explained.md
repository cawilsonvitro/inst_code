{    "Tool_ip": {
        "192.168.1.1": "host",
        "192.168.1.2": "fourpp",
        "192.168.1.3": "hall",
        "192.168.1.4": "rdt",
        "192.168.1.5": "nearir",
        "127.0.0.1": "testing"
    },
    "Hall": {
        "sys": "HMS"
    },
    "RDT": {
        "sys":{
        "T_Bias_on": //"150.0", #temperature voltage and current come on 
        "t_run": "1", //unused was for total run time
        "t_delay": "1", //time between measurements 
        "fan_delay": "30", //unused was only used to move fan out
        "T_cool": "130", // temp to turn fan off
        "num_of_meas": "60"// number of measurements to make
        },
        "USB-9211A": {
            "Min_val": "-0.05",  //min current value
            "Max_val": "0.05" //make current value
        } 
    },
    "Nir":{
        "int_tim": "50", #integration time
        "scans_to_avg": "1",# number of reading to take
        "x_smooth": "0",
        "x_timing": "3"
    },
    "fourpp":{
        "resource_addy":"USB0::0xF4EC::0x1208::SDM36HCD801150::INSTR",
        "sample_count": "30" #number of readings to take
    },
    "Database_Config":{
        "host": "WHAMNUC1",
        "db": "glass_test",
        "driver": "{ODBC Driver 17 for SQL Server}"
    },
    "Tool_pre": {
        "fourpp": "fpp",
        "hall": "ha",
        "rdt": "rdt",
        "nearir": "nir",
        "test": "t"
    }
}
