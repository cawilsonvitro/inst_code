import json
import socket
import os
# import typing
import sys
import subprocess
import venv #type:ignore
import traceback

def spawn_program_and_die(program, exit_code=0):
    """
    Start an external program and exit the script 
    with the specified return code.

    Takes the parameter program, which is a list 
    that corresponds to the argv of your command.
    """
    # Start the external program
    # print("code to cmd", program)
    subprocess.Popen(program)
    # We have started the program, and can suspend this interpreter
    sys.exit(exit_code)
    
def venv_builder(req = "constraints.txt") -> None:
    """
    Creates a Python virtual environment in the current working directory and installs dependencies from a requirements file.
    This function performs the following steps:
    1. Reads the specified requirements file (default: "constraints.txt").
    2. Strips whitespace from each line and replaces any line containing "delcom" with a local wheel file path.
    3. Writes the processed requirements back to the file.
    4. Creates a new virtual environment in a ".venv" directory if it does not already exist.
    5. Installs the dependencies from the requirements file into the virtual environment using pip.
    Args:
        req (str, optional): Path to the requirements file. Defaults to "constraints.txt".
    Returns:
        None
    """
    
    lines: list[str]
    req_file:str = req
    with open( req_file, 'r') as f:
        lines = list(f.readlines())


    stripped_lines: list[str] = []
    stripped: str = ""
    cwd = os.getcwd()
    venv_path = os.path.join(cwd, '.venv') 
    if not os.path.exists(venv_path):
        for line in lines:
            stripped = line.strip()
            if "delcom" in stripped:
                stripped = "delcom @ file:///" + os.path.join(cwd,"install_files","delcom-0.1.1-py3-none-any.whl")
            if stripped != "":
                stripped_lines.append(stripped)

        with open(req_file, "w") as f:
            for line in stripped_lines:
                f.write("\n" + line)
                

        venv.create(venv_path, with_pip=True, clear=True)

        script = os.path.join(venv_path, 'Scripts')

        py = os.path.join(script, 'python.exe')

        pip = os.path.join(script, 'pip.exe')

        install = f"{py} {pip} install -r constraints.txt"

        os.system(install)
        
def launch():
    """
    Launches the appropriate tool script based on the current machine's IP address and configuration.
    This function reads configuration from 'config.json', determines the current machine's IP address,
    and selects the correct tool script to launch. It handles different tools (e.g., 'hall', 'fourpp', 'RDT')
    and their specific configurations, constructs the command-line arguments, and spawns the selected script
    using the Python interpreter from the local virtual environment.
    Raises:
        KeyError: If the current IP address is not found in the configuration, defaults to 'testing' mode.
    Side Effects:
        Launches a new process for the selected tool script and terminates the current process.
    """
    kwargs = []
    virt_path: str = os.path.join(os.getcwd(), '.venv', 'scripts', 'python.exe')

    with open ('config.json', 'r') as f:
        config = json.load(f)
    
    
    Tool_ip:dict[str, str] = config['Tool_ip']
    hall = config['Hall']["sys"]
    ver_map = Tool_ip.items()
    
    inv_map = {v: k for k, v in ver_map}
    server_ip = inv_map["host"]


    hostname:str = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    # ip_address: str = "127.0.0.1" #for debugging
    # print(f"Hostname: {hostname}")
    # print(f"IP Address: {ip_address}")

    try:
        tool: str = Tool_ip[ip_address]
    except KeyError:
        # print(f"IP address {ip_address} not found in config.json, tryind debugging ip")
        
        tool = "testing"


    file_name: str = "main"

    # print(tool)

    if tool != "host" and tool != "testing":
        if tool == "hall":
            if hall == "HMS":
                file_name = ""
                file_name += "hall_script"
            else:
                file_name += tool
        elif tool == "fourpp":
            fpp_config = config['fourpp']
            for key,value in fpp_config.items():
                # print(key,value)
                kwargs.append(f"{key}={value}")

            file_name += tool
            
        elif tool == "RDT":
            rdt_config = config['RDT']
            T_bias_on = rdt_config['t_bias']
            t_run = rdt_config['t_run']
            t_delay = rdt_config['t_delay']
            T_cool = rdt_config['T_cool']
            num_of_meas = rdt_config['num_of_meas']
            usbconfig = config['RDT']['USB-9211A']
            min_val = usbconfig['Min_val']
            max_val = usbconfig['Max_val']
            
            file_name += tool
        else:
            file_name += tool
        file_name = f"tools//{tool}//{file_name}"
        
    elif tool != "testing":
        file_name = f"{file_name}.py"

    # else:
    #     server_ip = "127.0.0.1"
    #     # file_name =  r"hall_v2_test\hall_script"
    #     # file_name += ".py"
    #     # file_name = f"tools//hall//{file_name}"
    py = virt_path
    if not file_name.endswith('.py'): file_name += '.py'
    if file_name != "testing":
        # print("FILENAME", file_name)
        program = [py, file_name, server_ip]
        for i in kwargs: program.append(i)
        spawn_program_and_die(program)



if __name__ == "__main__":
    sysargs = sys.argv
    # print(sysargs)
    try:
        if sysargs[-1] == "test":      
            with open ('config.json', 'r') as f:
                config = json.load(f)
                
                
        if sysargs[-1] == "build":
            venv_builder() #builds venv, requires internet connections
        elif sysargs[-1] == "launch+build":
            venv_builder()
            launch()
        elif sysargs[-1] == "launch":
            launch()
        else:
            sysargs.append("launch")
            launch()
    except Exception as e:
        print(traceback.format_exc())
        # print("I ran")

