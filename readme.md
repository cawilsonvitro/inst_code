

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

to do:

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

write script to handle copying files from docker container over to other computers which will ssh into docker container and copy files to repo

need to do full test with vdap

client reconnect in app and starts without tcp working

need to get it closing nicely

add sql installs to setup

auto update connection status when device connects

done:

tcp server cannot handel reconnecting need to fix

i dont need to thread indi. inst 

might be able to remove queue and have tcp handler hand sql stuff