import os
import sys
cwd = os.getcwd()
try:
    ip = sys.argv[1]
except:
    ip = "127.0.0.1"
# os.system(f"py hall_script.py {ip} pre")

os.system("cd \"C:\\Program Files (x86)\\HMS3000 V3.52\"")

os.system("\"C:\\Program Files (x86)\\HMS3000 V3.52\\HMS-3000 V3.52.exe\"")

os.system(f"cd {cwd}")

os.system(f"hall_script.exe {ip} post")
