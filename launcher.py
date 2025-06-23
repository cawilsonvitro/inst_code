import json
import socket
import os
import typing



file: typing.TextIO = open('config.json', 'r')
config:dict[str, str] = json.load(file)['Tool_ip']


hostname:str = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
# ip_address: str = "127.0.0.1" #for debugging
# print(f"Hostname: {hostname}")
# print(f"IP Address: {ip_address}")

try:
    tool: str = config[ip_address]
except KeyError:
    print(f"IP address {ip_address} not found in config.json.")
    tool = "" 


file_name: str = "main"

if tool != "host" and tool != "testing":
    
    file_name += tool

    file_name += ".py"

    file_name = f"tools//{tool}//{file}"
    
elif tool != "testing":
    file_name = f"{file_name}.py"

else:
    server_ip = "127.0.0.1"
    

server_ip = list(config.keys())[0]
if file_name != "testing":
    os.system(f"py {file_name} {server_ip}")




stop = True


