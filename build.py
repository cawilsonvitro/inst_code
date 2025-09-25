import json
import socket
import urllib.request


#installing python


#building exes and removing unneeded files

with open ('config.json', 'r') as f:
    config = json.load(f)

hostname:str = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
tool = config["Tool_ip"][ip_address]