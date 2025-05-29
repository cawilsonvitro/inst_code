import socket
import json

host = None

with open('config.json', 'r') as file:
    ips = json.load(file)["Tool_ip"]
    for key in list(ips.keys()):
        if ips[key] == "Host":
            host = key
            
            
            
print(host)



def client_program(host):
    host = host  # as both code is running on same pc
    port = 5000  # socket server port number

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    message = input(" -> ")  # take input

    while message.lower().strip() != 'bye':
        client_socket.send(message.encode())  # send message
        data = client_socket.recv(1024).decode()  # receive response

        print('Received from server: ' + data)  # show in terminal

        message = input(" -> ")  # again take input

    client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program(host)