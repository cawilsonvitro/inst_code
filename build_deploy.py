#region imports
import os
import sys
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





if __name__ == "__main__":
    cwd = os.getcwd()
    exe_path = get_exe_location()
    if str(cwd).lower() != str(exe_path).lower():
        os.chdir(exe_path)
        print(f"Changed working directory to: {os.getcwd()}")
    
    