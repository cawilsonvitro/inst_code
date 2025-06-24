import json
import socket
import os
import typing
import sys
import subprocess


def spawn_program_and_die(program, exit_code=0):
    """
    Start an external program and exit the script 
    with the specified return code.

    Takes the parameter program, which is a list 
    that corresponds to the argv of your command.
    """
    # Start the external program
    subprocess.Popen(program)
    # We have started the program, and can suspend this interpreter
    sys.exit(exit_code)
    

if __name__ == "__main__":
    
    virt_path: str = os.path.join(os.getcwd(), '.venv', 'scripts', 'python.exe')

    file: typing.TextIO = open('config.json', 'r')
    config:dict[str, str] = json.load(file)['Tool_ip']


    hostname:str = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    # ip_address: str = "127.0.0.1" #for debugging
    # print(f"Hostname: {hostname}")
    # print(f"IP Address: {ip_address}")

    try:
        tool: str = config[ip_address]
        print(tool)
    except KeyError:
        print(f"IP address {ip_address} not found in config.json.")
        tool = "" 


    file_name: str = "main"



    if tool != "host" and tool != "testing":
        
        file_name += tool
        file_name += ".py"
        file_name = f"tools//{tool}//{file_name}"
        
    elif tool != "testing":
        file_name = f"{file_name}.py"

    else:
        server_ip = "127.0.0.1"

    print(file_name)
    py = virt_path
    server_ip = list(config.keys())[0]
    if file_name != "testing":
        spawn_program_and_die([py, file_name, server_ip])


    stop = True


