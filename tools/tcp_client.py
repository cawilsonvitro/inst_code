

import socket
import sys
from multiprocessing import Queue
from queue import Empty
from typing import Any

SERVER = "127.0.0.1" #"192.168.1.1"
PORT = 5050
ADDR = (SERVER, PORT)


class client():
    def __init__(self, ip, port, msg_in : Queue[Any], msg_out: Queue[Any]):
        self.ADDR = (ip, port)
        
        self.data = ""
        self.flag = 0
        self.tool = ""
        
        self.soc = None
        
        
        
    def load_config(self):
        
        self.commands_func= {"ID" :self.id,
            
        }
        
        self.commands = list(self.commands_func.keys())
        


    def connect(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.soc.connect(self.ADDR)

        except OSError or ConnectionRefusedError:
            print(
            "\nPlease check if the server is connected to the internet\n"
            "and that the IP and PORT numbers are correct on both ends\n"
            )
            sys.exit()
            
    def disconnect(self):
        self.soc.send("Q".encode())
        self.soc.close()
            
    def id(self):
        '''
        gets id of client
        '''
        if self.tool == "":
            self.soc.send(self.commands[0].encode())
            
            self.tool = self.soc.recv(1024).decode()
            print(self.tool)
        else:
            return self.tool
        
    def measure(self):
        '''
        gets measurement from tool and sends it over
        '''
        
        #put getting command from queue here 
        
        sample_value = 98571
        
        self.soc.send(str(sample_value).encode())

        resp = self.soc.recv(1024).decode()
        
        if resp == "data received":
            print("data sent")
        
    def run_client(self):
        '''
        runs the client in a loop, main purp is to keep getting data from client
        '''
        while self.data != "QUIT":
            if self.flag == 0:
                self.connect()
                print(f"Instrument connected to {self.ADDR[0]}")
                flag += 1
                
                
                

if __name__ == "__main__":
    temp = client(SERVER, PORT)
    
    temp.load_config()
    
    temp.connect()
    
    temp.id()
    
    temp.measure()
    
    temp.disconnect()
    print("I RAN")