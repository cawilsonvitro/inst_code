tcp notes
measuring
1st. Client Requests meta data of sample, if no sample returns blank
2nd. Client update meta data of sample if needed
3rd. Client carries out measurement procedure 
protocol for sample


to use nidaq systems run
python -m pip install nidaqmx

python -m nidaqmx installdriver

logging: most larger things and things running in the app of the intrument will be in logging.info others will be in logging.debugging


git notes: 
connect with the following:
ssh cawilson@vitro.com@127.0.0.1

to run with virtual env us .venv\Scripts\python.exe <path to python script>


to fix 2503/2502:
go to Navigate to the Windows Temp folder located at c:\windows\temp and give permissions to user

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


V3:
settings window
tools in one package
tcp improvement
change string builders to (",").join func
add automatic reinit to ddrivers



to do:
main: add command that is sent to a tool to clear all data
and log and data clearing 

main: test sql and run before moving over
main: add operator id columns to database building


all tools: slow main boot
all tools: make sure we are not calling config and that we are using sysv args to pass args from launcher
fpp: make sure new config layout works with code

hall: debug script again and get running with hall computer


RDT: get slow start fixed
RDT: get repeated measure to graph name
RDT: get tcp stuff up
RDT: get data saving
RDT :fix graph lag
RDT: get closing graph support

change timers to match JIMS leave mine as comments and talk to

get list of params we can changes

improve logging in all tools


add instrument settups to config

add math to nearir

add better logging to inst utils

for hall script if it fails to write to server it reverts the file (I don't know if this is needed test)
add file manager to other tools

add better data storage to rdt for future ai stuff

need to update setup.py 

(last)go through and remove dubugging prints
(last) remove Any typing
(last) update gitignore

add to setup.py:
    adjust venv pyvevn.cfg to target exe

build plant system
add better error handling


need to do full test with vdap

test installs and fix them

add sql installs to setup


done:
add pos to tcp protocol during "META" 

RDT: fix conifg with launcher

propagate v2

fix setup and make it runoffline

clean up imports

add time outs to sending 

get working with getting server from config

update venv builder to update declome file path automatically
clients close poorly
clients don't work without tcp connection
clients don't reconnect to server 
add logging
redo way to change status light
StandardLabel.instances["fourpp_status"].configure(image = TkImage("fourpp_status", r"images\Status_Bad.png").image)
reduce file open and closing
need to get sql server better

add front end functionality to main

get better status lights working


server crashes if client closes while waiting 


add reconnect

add logging to server 

four pp reconnect is not auto updating

auto update connection status when device connects

package up the file manager and tcp client and other packages want most into packages

add sample id to input field on 4 pp

need to get it closing nicely

client reconnect in app 

need to get execution working with virt 

file management system

get local debugging working again just changes 127.0.0.1 to all ip

tcp server cannot handel reconnecting need to fix

i dont need to thread indi. inst 

might be able to remove queue and have tcp handler hand sql stuff

figure out better launching method currently using systems python to launch venv python

fix pathing to working with venv paths 


update script to work with venv to bypasss other stuff

starts without tcp working

fix issues with tcp protcol not being very robust