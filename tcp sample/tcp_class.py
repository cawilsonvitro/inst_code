#region imports
import socket
import select
import time
import random
from multiprocessing import Process, Queue
from queue import Empty
from typing import Any
#endregion 





class tcp_multiserver():
    def __init__(self, ip, port, bus, max_connections=5):
        self.addr = (ip, port)
        self.max_connections = max_connections
        self.server_socket = None
        self.connected_sockets = []  # list of the client sockets being connected
        
        self.starttime = None
        self.server_socket = None
        
        self.bus_out: Queue[Any] = bus
        
    def all_sockets_closed(self):
        """closes the server socket and displays the duration of the connection"""
        print("\n\nAll Clients Disconnected\nClosing The Server...")
        endtime = time.time()
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
            print("\t", c.getpeername())  # ('IP', PORT)
            
    def serve_client(self, current_socket):
        """Takes the msg received from the client and handles it accordingly"""
        try:
            client_data = current_socket.recv(1024).decode()
            self.bus_out.put(client_data)  # send the message to the bus
            date_time = time.strftime("%d/%m/%Y, %H:%M:%S")
            print(
                f"\nReceived new message form client {current_socket.getpeername()} at {date_time}:"
            )

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
            # if the client asks to disconnect, he sends the word "quit" and the server response with "Bye" message.
            # and when the client receives this message it automatically disconnects from the server.
            # we also know that the server response back the messages received the client.
            # so we want to make sure that if the client sends to word "Bye", the server wont send the exact same message,
            # and therefore wont force the client to disconnect.

            elif client_data.upper() == "NAME":  # send server's name
                current_socket.send("SERVER'S NAME: LOCAL HOST - MY PC".encode())
                print("Responded by: Sending The Name of the Server")

            elif client_data.upper() == "TIME":  # send current time and date
                current_time = f"Today is {time.strftime('%A %d %b %Y %I:%M:%S')}"
                current_socket.send(current_time.encode())
                print("Responded by: Sending current time and date")

            elif client_data.upper() == "RAND":  # send random number between 0 and 10
                random_number = str(round(10 * (random.random())))
                current_socket.send(f"Your random number is: {random_number}".encode())
                print(
                    f"Responded by: Sending a random number between 0-10: {random_number}"
                )

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
                current_socket.send(client_data.encode())
                print("Responded by: Sending the message back to the client")
    
    def setup_server(self):
        """server setup and socket handling"""
        print("Setting up server...")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setblocking(False)  # set the server socket to non-blocking mode
        self.server_socket.bind(self.addr)
        print("\n* Server is ON *\n")
        print("Waiting for clients to establish connection...")
        self.starttime = time.time()
           
    def start_server(self):
        self.bus_out.put("Server Started")
        self.server_socket.listen()
        print(f"Server is listening on {self.addr[0]}:{self.addr[1]}")
        try:
            while True:
                ready_to_read, ready_to_write, in_error = select.select(
                    [self.server_socket] + self.connected_sockets, [], [], 0
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
                    self.serve_client(current_socket)
                #  print("\n\nWaiting for clients to connect...\n")

        except ValueError:
            # occurs when the last client connected is forcibly closing the socket (and not by Sending 'q' or 'quit'),
            # and the server keeps scanning with the 'select()' method.
            # In this case the select method will return -1 and raise an exception for value error.
            # we know that this exception can be raised only when the list of connected sockets is empty, so we will call a function to close the server socket.

            self.all_sockets_closed()
            
        except Exception as e:
            # catch any other exception that may occur
            print(f"An error occurred: {e}")
            self.all_sockets_closed()


# SERVER = "192.168.1.1"
# PORT = 5050
# ADDR = (SERVER, PORT)

# temp = tcp_multiserver(SERVER, PORT)
# temp.setup_server()
# temp.start_server()
