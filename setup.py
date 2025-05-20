#run this file in python to run the command
import os
import subprocess as sp
import urllib.request
import zipfile
import urllib
import ssl
import winreg

ssl._create_default_https_context = ssl._create_unverified_context

def check_programs(program):
    found = False
    reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    key = winreg.OpenKey(reg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")

    for i in range(winreg.QueryInfoKey(key)[0]):
        software_key_name = winreg.EnumKey(key, i)
        software_key = winreg.OpenKey(key, software_key_name)
        try:
            software_name = winreg.QueryValueEx(software_key, "DisplayName")[0]
            if program in software_name:
                print("Found ", program, software_name)
                found = True 
                return found
        except Exception as e:
            print(e)
    
    return found

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

        fileout = os.getcwd()  + "\\" + "\\install_files\\" + fileout
        sp.run(('cmd', '/C', 'start', '', fileout))

        print("install complete")



#region Local exes
locals = ["NI IVI Compliance Package", "NI VISA"]
locals_paths = ["install_files\ni-icp_25.3_online.exe", "install_files\ni-visa_25.3_online.exe"]
i = 0 
for local in locals:
    if check_programs(local):
        print("software already installed")
    else:
        os.system(locals_paths[i])
        
    i += 1
#region Online exes
urls = ["https://siglentna.com/download/44281/?tmstv=1747753775",
        "https://siglentna.com/download/46709/?tmstv=1747767986"]
paths = ["install_files/SDM IVI Drivers_V2.5.zip",
         "install_files/EasyDMMX_V1.0.3.zip"]
names = ["Siglent Driver",
         "Siglent Software"]

onlines = ["SDM IVI Drivers", "EasyDMMX"]

i = 0
for online in onlines:
    if check_programs(online):
        print("software already installed")
    else:
        download_unzip(urls[i], paths[i], names[i])
    i += 1

#end region


#region Clean up

#end region
