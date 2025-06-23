

import socket
import sys
from multiprocessing import Queue
from queue import Empty
from typing import Any
import time

SERVER = "192.168.1.1" #"127.0.0.1" #
PORT = 5050
ADDR = (SERVER, PORT)


class client():
    def __init__(self, ip, port):#, msg_in: Queue, msg_out: Queue):
        self.ADDR = (ip, port)
        
        self.data = ""
        self.flag = 0
        self.tool = ""
        
        self.soc = None
        
        # self.msg_in = msg_in
        # self.msg_out = msg_out

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
            self.soc.send("ID".encode())
            
            self.tool = self.soc.recv(1024).decode()
            print(self.tool)
        else:
            return self.tool
        
   