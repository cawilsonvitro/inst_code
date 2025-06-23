import os
import sys



virt_path = os.path.join(os.getcwd(), 'suite', 'inst_code', 'virt', 'scripts', 'Activate.ps1')


os.system(f"\"powershell {virt_path}\"")

print(virt_path)