import json
import socket
import os
import typing



file: typing.TextIO = open('config.json', 'r')
config:dict[str, str] = json.load(file)['Tool_ip']


hostname:str = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
# print(f"Hostname: {hostname}")
# print(f"IP Address: {ip_address}")

try:
    tool: str = config[ip_address]
except KeyError:
    print(f"IP address {ip_address} not found in config.json.")
    tool = "" 


file_name: str = "main"

if tool != "host":
    file_name += tool

    file_name += ".py"

    file_name = f"tools//{tool}//{file}"
else:
    file_name = f"{file_name}.py"
    
server_ip = list(config.keys())[0]
os.system(f"py {file_name} {server_ip}")



stop = True