set mypath=%cd%s
py hall_script.py a pre
pause
cd "C:\Program Files (x86)\HMS3000 V3.52\"
"HMS-3000 V3.52.exe"
echo %mypath%
pause
cd %mypath%
py hall_script.py a post
pause