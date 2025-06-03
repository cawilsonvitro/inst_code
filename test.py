# # # def fun(**kwargs):
# # #     t = kwargs
# # #     for k, val in kwargs.items():
# # #         print("%s == %s" % (k, val))



# # # fun(s1 = 1, s2 = 1)


# # # if '64' in 'SDM 3k4k IVIDmm V2.5_EN/sdm_ivi_v2.5_32bit.msi':
# # #     print("HUH")
    
# # # import winreg

# # # # reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
# # # # key = winreg.OpenKey(reg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")

# # # # for i in range(winreg.QueryInfoKey(key)[0]):
# # # #     software_key_name = winreg.EnumKey(key, i)
# # # #     software_key = winreg.OpenKey(key, software_key_name)
# # # #     try:
# # # #         software_name = winreg.QueryValueEx(software_key, "DisplayName")[0]
# # # #         if "NI IVI Compliance Package" in software_name:
# # # #             print("Found NI IVI Compliance Package", software_name)
# # # #         if "NI-VISA" in software_name:
# # # #             print("Found NI-VISA", software_name)
# # # #         if "EasyDMMX" in software_name:
# # # #             print("EasyDMMX", software_name)
# # # #     except Exception as e:
# # # #         print(e)



# # # # reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
# # # # key = winreg.OpenKey(reg, r"SOFTWARE\WOW6432Node\National Instruments\Common\Installer\Parts")
                     
# # # # for i in range(winreg.QueryInfoKey(key)[0]):
# # # #     software_key_name = winreg.EnumKey(key, i)
# # # #     software_key = winreg.OpenKey(key, software_key_name)
# # # #     try:
# # # #         software_name = winreg.QueryValueEx(software_key, "ProductName")[0]
# # # #         if "SDM IVI" in software_name:
# # # #             print("Found sdm ivi", software_name)
# # # #     except Exception as e:
# # # #         print(e)

# # # # reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
# # # # key = winreg.OpenKey(reg, r"SOFTWARE\Classes\.dmm")

# # # # for i in range(winreg.QueryInfoKey(key)[0]):
# # # #     software_key_name = winreg.EnumKey(key, i)
# # # #     software_key = winreg.OpenKey(key, software_key_name)
# # # #     try:
# # # #         software_name = winreg.QueryValueEx(software_key, "EasyDMM-XFile.dmm")[0]
# # # #         print("Found EasyDMM-XFile.dmm", software_name)
# # # #     except Exception as e:
# # # #         print(e)
                  
# # # def check_programs(program, keyname, query):
# # #     found = False
# # #     reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
# # #     key = winreg.OpenKey(reg, keyname)#r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")

# # #     for i in range(winreg.QueryInfoKey(key)[0]):
# # #         software_key_name = winreg.EnumKey(key, i)
# # #         software_key = winreg.OpenKey(key, software_key_name)
# # #         try:
# # #             software_name = winreg.QueryValueEx(software_key, query)[0]
# # #             if "DMM-X" in query:
# # #                 print("Found DMM-X", software_name)
# # #                 found = True
# # #                 return found
# # #             else:   
# # #                 if program in software_name:
# # #                     print("Found ", program, software_name)
# # #                     found = True 
# # #                     return found
# # #         except Exception as e:
# # #             print(e)
    
# # #     return found

# # # print(check_programs("SDM IVI", r"SOFTWARE\Classes\.dmm", "EasyDMM-XFile.dmm"))

# # # # import os

# # # # # Directory path
# # # # dir_path = r"install_files\SDM 3k4k IVIDmm V2.5_EN"

# # # # # List all files in the directory
# # # # for filename in os.listdir(dir_path):
# # # #     file_path = os.path.join(dir_path, filename)
    
# # # #     # Check if it is a file (not a subdirectory)
# # # #     if os.path.isfile(file_path):
# # # #         os.remove(file_path)  # Remove the file
# # # #         print(f"Deleted file: {filename}")

# # # # os.rmdir(dir_path)  # Remove the directory


# # import sys

# # print(sys.argv)


# # from multiprocessing import Process, Queue


# # a = Queue()

# # a.put("Hello from main process")

# # b = a.get()

# # print(b)


# def a():
#     return 1

# def b():
#     return 2


# adc = {"a": a,
#        "b": b}

# print(adc["a"]())


# import queue
# from multiprocessing import Queue


# e = Queue(maxsize=1)

# e.put("A")

# e.put("B")

import socket

def internet(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False

print(internet())




import random
import time

from matplotlib import pyplot as plt
from matplotlib import animation


class RegrMagic(object):
    """Mock for function Regr_magic()
    """
    def __init__(self):
        self.x = 0
    def __call__(self):
        time.sleep(random.random())
        self.x += 1
        return self.x, random.random()

regr_magic = RegrMagic()

def frames():
    while True:
        yield regr_magic()

fig = plt.figure()

x = []
y = []
def animate(args):
    x.append(args[0])
    y.append(args[1])
    return plt.plot(x, y, color='g')


anim = animation.FuncAnimation(fig, animate, frames=frames, interval=1000)
plt.show()
print("I ran")