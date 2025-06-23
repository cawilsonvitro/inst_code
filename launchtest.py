import os
import sys



virt_path = os.path.join(os.getcwd(), '.venv', 'scripts', 'python.exe')


os.system(f"{virt_path} test.py")

print(virt_path)