import json
import socket
import os

with open('config.json', 'r') as file:
    config = json.load(file)['Tool_ip']


hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
print(f"Hostname: {hostname}")
print(f"IP Address: {ip_address}")

try:
    tool = config[ip_address]
except KeyError:
    print(f"IP address {ip_address} not found in config.json.")
    tool = None 

file = "main"

if tool != "Host":
    file += tool

file += ".py"

os.system(f"py {file} ip_address ")



stop = True