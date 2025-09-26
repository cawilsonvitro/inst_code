import urllib.request
import subprocess as sp
import os
import zipfile

url = "https://siglentna.com/download/46709/?tmstv=174776798"
path = "install_files/EasyDMMX_V1.0.3.zip"
# urllib.request.urlretrieve(url, path)


def download_unzip(url, path , name):
    print('Downloading ', name)
    urllib.request.urlretrieve(url, path)
    print("Download completed")

    print("unzipping ", name)

    with zipfile.ZipFile(path, 'r') as zip:
        for file in zip.filelist:
            if ".exe"in file.filename:
                fileout = file.filename
                print(fileout)
                break
            if "64" in file.filename or "64bit" in file.filename:
                if ".msi" in file.filename:
                    fileout = file.filename
                    print(fileout)
                    break
        zip.extractall("install_files")

        print("running ", name, "installer")

        fileout = os.getcwd()  + "\\" + "install_files\\" + fileout
        sp.run(('cmd', '/C', 'start', '', fileout))

        print("install complete")
        return fileout
        

download_unzip(url, path, "EasyDMM-X")



# import winreg
# import os

# # reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
# # key = winreg.OpenKey(reg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")

# # for i in range(winreg.QueryInfoKey(key)[0]):
# #     software_key_name = winreg.EnumKey(key, i)
# #     software_key = winreg.OpenKey(key, software_key_name)
# #     try:
# #         software_name = winreg.QueryValueEx(software_key, "DisplayName")[0]
# #         print(software_name)
# #     except Exception as e:
# #         print(e)
        
        

# def check_programs(program, keyname, query):
#     found = False
#     if "DMM-X" not in query: #this is done because they do not have a registry entry with values and registry doesn't get removed but 
#         #path does
#         reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
#         key = winreg.OpenKey(reg, keyname)#r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")

#     for i in range(winreg.QueryInfoKey(key)[0]):
#         software_key_name = winreg.EnumKey(key, i)
#         software_key = winreg.OpenKey(key, software_key_name)
#         try:
#             software_name = winreg.QueryValueEx(software_key, "DisplayName")[0]
#             if program in software_name:
#                 print("Found ", program, software_name)
#                 found = True 
#                 return found
#         except Exception as e:
#             print(e)
#     else:
#         found = os.path.isdir(r"C:\Program Files (x86)\EasyTools\EasyDMM-X")
#         print("Found EasyDMM-X", query)
#         return found
#     print("not found")
#     return found


# check_programs('NI IVI Compliance Package', r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", "")
# check_programs("NI-VISA", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", "")
# check_programs("SDM IVI", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", "")