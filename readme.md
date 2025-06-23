git notes: 
connect with the following:
ssh cawilson@vitro.com@127.0.0.1

sql: for debugging
WHAMNUC1

for 4 pp
First installed
https://www.ni.com/en/support/downloads/drivers/download.ivi-compliance-package.html?srsltid=AfmBOoq6J4W_o6OnaM8dM2qVdWaU9a3JQMW0jFE53bZjrWgZ-QUobpDT#564292

First installed drivers then software from here
https://siglentna.com/service-and-support/firmware-software/ 


Usb resource addy
USB0::0xF4EC::0x1208::SDM36HCD801150::INSTR

tcp server based on 
https://github.com/YanivWein24/TCP_Server_Client/blob/master/TCP_Client.py

to activate use Activate.ps1 in the venv folder

make sure Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

make sure to replace in .venv\pyvenv.cfg the c### with current user


to do:

figure out better launching method currently using systems python to launch venv python

(last) remove Any typing
(last) update gitignore

add way to auto select or have user select which hall system we are going to use
code both

get eptoc bus


add to setup.py:
    adjust venv pyvevn.cfg to target exe



fix pathing to working with venv paths 



need to get execution working with virt 

get setup working with windows 11 computers

update script to work with venv to bypasss other stuff
add sample id to input field on 4 pp

need to get sql server better

add front end functionality to main

get better status lights working

add hard typing 

add better error handling

file management system

clean up imports


need to do full test with vdap

 starts without tcp working

need to get it closing nicely

add sql installs to setup

auto update connection status when device connects

done:

client reconnect in app 


get local debugging working again just changes 127.0.0.1 to all ip

tcp server cannot handel reconnecting need to fix

i dont need to thread indi. inst 

might be able to remove queue and have tcp handler hand sql stuff