def fun(**kwargs):
    t = kwargs
    for k, val in kwargs.items():
        print("%s == %s" % (k, val))



fun(s1 = 1, s2 = 1)


if '64' in 'SDM 3k4k IVIDmm V2.5_EN/sdm_ivi_v2.5_32bit.msi':
    print("HUH")
    
import winreg

reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
key = winreg.OpenKey(reg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")

for i in range(winreg.QueryInfoKey(key)[0]):
    software_key_name = winreg.EnumKey(key, i)
    software_key = winreg.OpenKey(key, software_key_name)
    try:
        software_name = winreg.QueryValueEx(software_key, "DisplayName")[0]
        if "NI IVI Compliance Package" in software_name:
            print("Found NI IVI Compliance Package", software_name)
    except Exception as e:
        print(e)

