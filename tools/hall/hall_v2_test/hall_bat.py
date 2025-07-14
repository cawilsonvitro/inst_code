import os
import sys
import json




if __name__ == "__main__":
    cwd = os.getcwd()
    if "hall" in cwd:
        config_path = ("\\").join(cwd.split("\\")[:-3]) + "\\config.json"
    else:
        config_path = "config.json"
        cwd = cwd + "\\tools\\hall\\hall_v2_test"
    
    try:
        ip = sys.argv[1]
    except:
        with open(config_path) as f:
            ver_map: dict[str, dict[str, str]] = json.load(f)["Tool_ip"].items()
            inv_map = {v: k for k, v in ver_map}
            ip = inv_map["host"]

    # os.system(f"py hall_script.py {ip} pre")

    os.system("cd \"C:\\Program Files (x86)\\HMS3000 V3.52\"")

    os.system("\"C:\\Program Files (x86)\\HMS3000 V3.52\\HMS-3000 V3.52.exe\"")
    
    print(cwd)
    
    os.chdir(cwd)
    
    os.system(f"py hall_script.py {ip} post")
