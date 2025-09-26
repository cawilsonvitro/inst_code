#region imports
import os
import sys
import PyInstaller.__main__
import shutil
#endregion


def get_exe_location():
    """
    Returns the absolute path to the compiled executable.
    """
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        return os.path.dirname(sys.executable)
    else:
        # Running as a regular Python script
        return os.path.dirname(os.path.abspath(__file__))


def compile(script, path):
    PyInstaller.__main__.run([
    f'{script}',
    '--onefile',
    f'--distpath={path}',
    ])

import os
import shutil
import os.path


def deploy(tool):
    #region file strucutre
    deploy_path = f"dist/{tool}_deployment"
    tool_pypath = os.getcwd() + f"/tools/{tool}"
    
    if os.path.exists(deploy_path):
        shutil.rmtree(deploy_path)
    
    os.makedirs(deploy_path)
    os.makedirs(f"{deploy_path}/tools")
    os.makedirs(f"{deploy_path}/logs")
    shutil.copytree(r"install_files", f"{deploy_path}/install_files")
    
    i = 0
    for dirs,folders,files in os.walk(tool_pypath):
        if "__pycache__" not in dirs:
            if i != 0:
                if "images" in dirs:   
                    shutil.copytree(f"{dirs}", f"{deploy_path}/tools/{tool}/images")
                else:
                    end = dirs.split('\\')[-1]
                    print(f"{dirs}", "to", f"{deploy_path}/tools/{tool}/{end}")
                    os.makedirs(f"{deploy_path}/tools/{tool}/{end}", exist_ok=True)
        i += 1
    if tool != "main":
        tool_path = f"{deploy_path}/tools/{tool}/"
    dist_py =  f"{deploy_path}/tools/{tool}/main{tool}.py"
    dist_launcher = f"{deploy_path}/launcher.py"
    dist_setup = f"{deploy_path}/setup.py"
    shutil.copyfile("launcher.py", dist_launcher)
    shutil.copyfile("setup.py", dist_setup)
    shutil.copyfile("config.json", f"{deploy_path}/config.json")
    shutil.copyfile(f"{tool_pypath}/main{tool}.py", dist_py)
    #endregion
    
    #region building exes
    compile(f"{tool_pypath}/main{tool}.py", f"{deploy_path}/tools/{tool}/")
    compile("launcher.py", deploy_path)
    compile("setup.py", deploy_path)
    #endregion
    #region cleaning up
    to_remove = [dist_py, dist_launcher, dist_setup]
    
    for item in to_remove:
        if os.path.exists(item):
            os.remove(item)
    #endregion
    



if __name__ == "__main__":
    cwd = os.getcwd()
    exe_path = get_exe_location()
    if str(cwd).lower() != str(exe_path).lower():
        os.chdir(exe_path)
        print(f"Changed working directory to: {os.getcwd()}")
    tool = sys.argv[1] if len(sys.argv) > 1 else "fourpp"
    deploy(tool)

