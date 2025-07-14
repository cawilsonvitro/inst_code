import json
import socket
import os
import typing
import sys
import subprocess
import venv #type:ignore

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
    
def venv_builder(req = "constraints.txt") -> None:
    
    lines: list[str]
    req_file:str = req
    with open( req_file, '+r') as f:
        lines = list(f.readlines())


    stripped_lines: list[str] = []
    stripped: str = ""
    cwd = os.getcwd()
    venv_path = os.path.join(cwd, '.venv') 
    if not os.path.exists(venv_path):
        for line in lines:
            stripped = line.strip()
            if "delcom" in stripped:
                stripped = "delcom @ file:///" + os.path.join(cwd,"delcom-0.1.1-py3-none-any.whl")
            if stripped != "":
                stripped_lines.append(stripped)

        with open(req_file, "+w") as f:
            for line in stripped_lines:
                f.write("\n" + line)
                

        venv.create(venv_path, with_pip=True, clear=True)

        script = os.path.join(venv_path, 'Scripts')

        py = os.path.join(script, 'python.exe')

        pip = os.path.join(script, 'pip.exe')

        install = f"{py} {pip} install -r constraints.txt"

        os.system(install)
        
def launch():
    """_summary_ launches correct path
    """
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

if __name__ == "__main__":
    sysargs = sys.argv
    try:
        if sysargs[-1] == "build":
            
            venv_builder() #builds venv, requires internet connections
        if sysargs[-1] == "launch+build":
            print("I ran")
            venv_builder()
            launch()
        if sysargs[-1] == "launch":
            launch()
            
    except IndexError:
        launch()


