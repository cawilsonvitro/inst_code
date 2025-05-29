#run this file in python to run the command
import os
import subprocess as sp
import urllib.request
import zipfile
import urllib
import ssl
import winreg
import time


ssl._create_default_https_context = ssl._create_unverified_context

def check_programs(program, keyname, query):
    found = False
    if "DMM-X" not in query: #this is done because they do not have a registry entry with values and registry doesn't get removed but 
        #path does
        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        key = winreg.OpenKey(reg, keyname)#r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")

        for i in range(winreg.QueryInfoKey(key)[0]):
            software_key_name = winreg.EnumKey(key, i)
            software_key = winreg.OpenKey(key, software_key_name)
            try:
                software_name = winreg.QueryValueEx(software_key, query)[0]
                if program in software_name:
                    print("Found ", program, software_name)
                    found = True 
                    return found
            except Exception as e:
                pass
    else:
        found = os.path.isdir(r"C:\Program Files (x86)\EasyTools\EasyDMM-X")
        print("Found EasyDMM-X", query)
        return found
    print("not found")
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
        return fileout

def cleanup(dir):
    # List all files in the directory
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        
        # Check if it is a file (not a subdirectory)
        if os.path.isfile(file_path):
            os.remove(file_path)  # Remove the file
            print(f"Deleted file: {filename}")
    os.rmdir(dir)  # Remove the directory
    #region Local exes
locals = ["NI IVI Compliance Package", "NI-VISA"]
locals_paths = ["install_files\ni-icp_25.3_online.exe", "install_files\ni-visa_25.3_online.exe"]
keyname = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
query = "DisplayName"
i = 0 

for local in locals:
    if check_programs(local, keyname, query):
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

onlines = ["SDM IVI", "EasyDMMX"]

keynames = [r"SOFTWARE\WOW6432Node\National Instruments\Common\Installer\Parts", r"SOFTWARE\Classes\.dmm"]

querys = ["ProductName", "EasyDMM-XFile.dmm"]
unzipped_files = []
i = 0
for online in onlines:
    if check_programs(online, keynames[i], querys[i]): 
        print("software already installed")
    else:
        unzipped_files.append(download_unzip(urls[i], paths[i], names[i]))
    i += 1

#endregion


#region Clean up
for path in paths:
    try:
        os.remove(path)
    except Exception as e:
        print(e)
        print("file not found")

if unzipped_files != []:
    for unzip in unzipped_files:
        cleanup(unzip)
else:
    subfolders = [ f.path for f in os.scandir("install_files") if f.is_dir() ]
    if subfolders != []:
        for subfolder in subfolders:
            cleanup(subfolder)
stop = True
#endregion

#region pip
os.system("pip install -r requirements.txt")
print("pip install complete")