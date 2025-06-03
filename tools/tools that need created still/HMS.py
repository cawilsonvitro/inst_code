import subprocess as sp
import os
import signal
import psutil
import time



#this works but so messy get working with one lib
exepath = r"C:\Program Files (x86)\HMS3000 V3.52\HMS-3000 V3.52.exe"

p = sp.Popen(exepath)

#os.kill(p.pid, signal.SIGTERM)


while psutil.pid_exists(p.pid):
    print("hi")
