import os
import sys



virt_path = os.path.join(os.getcwd(), 'suite', 'inst_code', 'virt', 'scripts', 'python.exe')


os.system(f"\"powershell {virt_path}\" test.py")

print(virt_path)