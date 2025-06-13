#region imports
import socket
import select
import time
import dbhandler

from multiprocessing import Process, Queue #type:ignore
from queue import Empty #type:ignore
from typing import Any
import json
#endregion 





class tcp_multiserver():
    
    def __init__(self, ip:str , port:str , bus_out , bus_in, max_connections:int = 5):
        self.ADDR: tuple[str, str] = (ip, port)
        self.max_connections: int = max_connections
        self.server_socket: socket.socket
        self.connected_sockets: list[socket.socket] = []  # list of the client sockets being connected
        
        self.starttime: float
        
        #data management
        self.client_data: str
        self.bus_out = bus_out
        self.bus_in = bus_in
        self.SQL: dbhandler.sql_client = dbhandler.sql_client("config.json")

        
        #client ids
        self.read_to_read: list[socket.socket] = []
        
        #connection flags
        self.network_status:bool = False
        self.db_status:bool = False
        
        with open('config.json', 'r') as file:
            self.config = json.load(file)['Tool_ip']
        self.tools: dict[str, str] = {}
        
        for key in list(self.config.keys()): #type:ignore
            self.tools[f"{key}_incoming"] = False #type:ignore
        
        return
    
            
    def SQL_startup(self):
        try:
            self.SQL.load_config()
            self.SQL.connect()
            self.SQL.check_tables()
            self.db_status = True
        except Exception as e:
            print(e)
            self.db_status = False
            
        return
 
            
    def connections(self, host:str = "8.8.8.8", port: int = 53, timeout: int = 3):
        """
        Host: 8.8.8.8 (google-public-dns-a.google.com)
        OpenPort: 53/tcp
        Service: domain (DNS/TCP)
        """
        self.network_status = False
        self.db_status = False
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            self.network_status = True
        except socket.error as ex:
            print(ex)
            self.network_status = False
        try:
            self.db_status  = self.SQL.sql.closed
            
        except Exception as e:
            print(e)
            self.SQL_startup()
 
        
    def all_sockets_closed(self):
        """closes the server socket and displays the duration of the connection"""
        print("\n\nAll Clients Disconnected\nClosing The Server...")
        endtime: float = time.time()
        elapsed = time.strftime("%H:%M:%S", time.gmtime(endtime - self.starttime))
        unit = (
            "Seconds"
            if elapsed < "00:01:00"
            else "Minutes"
            if "01:00:00" > elapsed >= "00:01:00"
            else "Hours"
        )
        self.server_socket.close()
        print(f"\nThe Server Was Active For {elapsed} {unit}\n\n")
   
        
    def active_client_sockets(self):
        """prints the IP and PORT of all connected sockets"""
        print("\nCurrently Connected Sockets:")
        for c in self.connected_sockets:
            print("\t", c.getpeername())
  
    
    def serve_client(self, current_socket : socket.socket):
        """Takes the msg received from the client and handles it accordingly"""
        try:
            client_data = current_socket.recv(1024).decode()
           # self.bus_out.put(client_data)  # put the data in the bus for the main app to handle
          #  incoming = self.bus_in.get(timeout=5)  # wait for the main app to process the data
          #  print(incoming)
            date_time: str = time.strftime("%d/%m/%Y, %H:%M:%S")
       #     print(
        #        f"\nReceived new message form client {current_socket.getpeername()} at {date_time}:"
         #   )

        except ConnectionResetError:
            print(f"\nThe client {current_socket.getpeername()} has disconnected...")
            self.connected_sockets.remove(current_socket)
            current_socket.close()
            if len(self.connected_sockets) != 0:  # check for other connected sockets
                self.active_client_sockets()
            else:
                raise ValueError
            """the whole disconnection sequence is triggered from the exception handler, se we will just raise the exception
                    to close the server socket"""
        else:
            print(client_data)

            if client_data == "Bye":
                current_socket.send("bye".encode())
                print(
                    "Connection closed",
                )
            elif client_data == "ID":
                id: str = self.config[current_socket.getpeername()[0]]
                current_socket.send(id.encode())
            
            elif client_data == "MEAS":
                #first get tool to build SQL query with
                tool = self.config[current_socket.getpeername()[0]]
                print(f"awaiting value from {tool}")
                
                value = current_socket.recv(1024).decode()
                
                #get value
                
                value = float(value)
                
                print(value)
                
                #confirm
                print("Writing back")
                current_socket.send("data received".encode())
                
                
                #writing to sql server
                if tool == "fourpp":
                    values = [
                        ["resistance", str(value)],
                        ["sample_id", "123"]
                    ]
                    
                
                
                self.SQL.write(tool, values)
                    
                
                
                
                
            elif (
                client_data.upper() == "QUIT" or client_data.upper() == "Q"
            ):  # close connection with the client and close socket
                print(
                    f"Closing the socket with client {current_socket.getpeername()} now..."
                )
                current_socket.send("Bye".encode())
                # tell the client we accepted his request to disconnect, also disconnect the client from their side
                self.connected_sockets.remove(current_socket)
                current_socket.close()
                if len(self.connected_sockets) != 0:
                    self.active_client_sockets()
                else:
                    raise ValueError
                """the whole disconnection sequence is triggered from the exception handler, se we will just raise the exception
                    to close the server socket"""
            
            else:
                tool = current_socket.getpeername()[0]
                current_socket.send(client_data.encode())
             #   print("Responded by: Sending the message back to the client")
     
                
    def server(self):
        """server setup and socket handling"""
        print("Setting up server...")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.ADDR)

        self.server_socket.listen()
        print("\n* Server is ON *\n")
        print("Waiting for clients to establish connection...")
        self.starttime = time.time()
        self.connected_sockets = []  # list of the client sockets being connected
        while True:            
            try:       
                ready_to_read, ready_to_write, in_error = select.select(
                    [self.server_socket] + self.connected_sockets, [], []
                )                
                if len(ready_to_read) != 0:
                    for current_socket in ready_to_read:
                        if (
                            current_socket is self.server_socket
                        ):  # if the current socket is the new socket we receive from the server
                            (client_socket, client_address) = current_socket.accept()
                            print("\nNew client joined!", client_address)
                            self.connected_sockets.append(client_socket)
                            self.active_client_sockets()
                            continue
                        self.serve_client(current_socket)
            except ValueError:
                while len(self.connected_sockets) == 0:#while waiting for new clients
                                ready_to_read, ready_to_write, in_error = select.select(
                                [self.server_socket] + self.connected_sockets, [], []
                                )
                                
                                for current_socket in ready_to_read:
                                    if (
                                        current_socket is self.server_socket
                                    ):  # if the current socket is the new socket we receive from the server
                                        (client_socket, client_address) = current_socket.accept()
                                        print("\nNew client joined!", client_address)
                                        self.connected_sockets.append(client_socket)
                                        self.active_client_sockets()
                                        continue
            except KeyboardInterrupt:
                self.all_sockets_closed()
            except Exception as e:
                print(e)


    def quit(self):
        self.server_socket.close()
        self.SQL.quit()



if __name__ == "__main__":
    SERVER ="192.168.1.1" #"127.0.0.1"# 
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
        # Create an instance of the tcp_multiserver class         
    temp = tcp_multiserver(SERVER, PORT, a, b)
    temp.SQL_startup()
    temp.connections()
    # tcpthread = Process(target = temp.server)
    # counting_thread = Process(target=counting)
    # tcpthread.daemon = True  # Ensures the thread will exit when the main program exits
    # tcpthread.start()
    # counting_thread.start()
    
    # counting_thread.join()
    # tcpthread.join()
    
    a = 3
    # temp = tcp_multiserver(SERVER, PORT, a, b)
    # temp.server()



