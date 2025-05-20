#run this file in python to run the command
import os
import subprocess as sp
import urllib.request
import zipfile
import urllib
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


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

#region Online exes
urls = ["https://siglentna.com/download/44281/?tmstv=1747753775",
        "https://siglentna.com/download/4377/?tmstv=1747753775"]
paths = ["install_files/SDM IVI Drivers_V2.5.zip",
         "install_files/EasyDMMX_V1.0.3.zip"]
names = ["Siglent Driver",
         "Siglent Software"]

i = 0 

for url in urls:
    download_unzip(url,paths[i],names[i])
    i += 1
#end region




