import os
import time
from datetime import datetime as dt
import csv 
#only works if running from the same folder as the tool

class FileManager:
    def __init__(self, tool: str, size_lim: float) -> None:
        '''
        initializes the class and checks for data folder 
        '''
        self.tool = tool
        print(os.getcwd())
        self.path: str = os.path.join(os.getcwd(),"tools", tool, "data")
        if not os.path.exists(self.path):
            print("H")
            os.mkdir(self.path)    
        
        
        self.size_lim = size_lim #in gb
    #first check folder size
    
    def rotating_file_handler(self) -> None:
        #get file size
        byte_lim: float = float(self.size_lim) * 1024 * 1024 * 1024
        total_size = 0
        for dirpath,dirnames,filenames in os.walk(self.path):
           for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)                  
        
        if total_size > byte_lim:
            print("I ran")
            print("Rotating files")
            #sort files by date
            files = os.listdir(self.path)
            files.sort(key=lambda x: os.path.getmtime(os.path.join(self.path, x)))
            #delete oldest file
            oldest_file = os.path.join(self.path, files[0])
            os.remove(oldest_file)
            print(f"Deleted {oldest_file}")
    
    def write_data(self, sample_num: str, header: list[str], data: list[list[str | float | int]]) -> None:
        self.rotating_file_handler()
        self.date = dt.now().strftime("%m-%d-%Y, Hour %H Min %M Sec %S")
        
        file_name = f"{self.path}\\{sample_num}_{self.tool}_{self.date}.csv"
        
        with open(file_name, "w") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for row in data:
                writer.writerow(row)
        
        
        
if __name__ == "__main__":
    fm = FileManager('fourpp', 1)
    
    sample_num ="12345"
    header = ["Time", "value"]
    data = ["a","b"]
    
    temp = FileManager("fourpp","5")
    temp.write_data(sample_num, header, data)
    

    