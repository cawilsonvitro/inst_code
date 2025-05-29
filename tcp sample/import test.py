import socket
import select
import time
import random
from multiprocessing import Process, Queue
from queue import Empty
from typing import Any
import tcp_class as tcp

SERVER = "192.168.1.1"
PORT = 5050
ADDR = (SERVER, PORT)
a = Queue()
b = Queue()


def counting():
    count = 0
    while True:
        count += 1
        print(f"Count: {count}")
        time.sleep(1)  # Sleep to simulate work being done
        
        
if __name__ == "__main__":
    # Create an instance of the tcp_multiserver class         
    temp = tcp.tcp_multiserver(SERVER, PORT, a, b)
    tcpthread = Process(target = temp.server)
    counting_thread = Process(target=counting)
    tcpthread.daemon = True  # Ensures the thread will exit when the main program exits
    tcpthread.start()
    counting_thread.start()
    
    counting_thread.join()
    tcpthread.join()
    
    # temp = tcp_multiserver(SERVER, PORT, a, b)
    # temp.server()