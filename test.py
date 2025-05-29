# def fun(**kwargs):
#     t = kwargs
#     for k, val in kwargs.items():
#         print("%s == %s" % (k, val))



# fun(s1 = 1, s2 = 1)


# if '64' in 'SDM 3k4k IVIDmm V2.5_EN/sdm_ivi_v2.5_32bit.msi':
#     print("HUH")
    
# import winreg

# # reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
# # key = winreg.OpenKey(reg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")

# # for i in range(winreg.QueryInfoKey(key)[0]):
# #     software_key_name = winreg.EnumKey(key, i)
# #     software_key = winreg.OpenKey(key, software_key_name)
# #     try:
# #         software_name = winreg.QueryValueEx(software_key, "DisplayName")[0]
# #         if "NI IVI Compliance Package" in software_name:
# #             print("Found NI IVI Compliance Package", software_name)
# #         if "NI-VISA" in software_name:
# #             print("Found NI-VISA", software_name)
# #         if "EasyDMMX" in software_name:
# #             print("EasyDMMX", software_name)
# #     except Exception as e:
# #         print(e)



# # reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
# # key = winreg.OpenKey(reg, r"SOFTWARE\WOW6432Node\National Instruments\Common\Installer\Parts")
                     
# # for i in range(winreg.QueryInfoKey(key)[0]):
# #     software_key_name = winreg.EnumKey(key, i)
# #     software_key = winreg.OpenKey(key, software_key_name)
# #     try:
# #         software_name = winreg.QueryValueEx(software_key, "ProductName")[0]
# #         if "SDM IVI" in software_name:
# #             print("Found sdm ivi", software_name)
# #     except Exception as e:
# #         print(e)

# # reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
# # key = winreg.OpenKey(reg, r"SOFTWARE\Classes\.dmm")

# # for i in range(winreg.QueryInfoKey(key)[0]):
# #     software_key_name = winreg.EnumKey(key, i)
# #     software_key = winreg.OpenKey(key, software_key_name)
# #     try:
# #         software_name = winreg.QueryValueEx(software_key, "EasyDMM-XFile.dmm")[0]
# #         print("Found EasyDMM-XFile.dmm", software_name)
# #     except Exception as e:
# #         print(e)
                  
# def check_programs(program, keyname, query):
#     found = False
#     reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
#     key = winreg.OpenKey(reg, keyname)#r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")

#     for i in range(winreg.QueryInfoKey(key)[0]):
#         software_key_name = winreg.EnumKey(key, i)
#         software_key = winreg.OpenKey(key, software_key_name)
#         try:
#             software_name = winreg.QueryValueEx(software_key, query)[0]
#             if "DMM-X" in query:
#                 print("Found DMM-X", software_name)
#                 found = True
#                 return found
#             else:   
#                 if program in software_name:
#                     print("Found ", program, software_name)
#                     found = True 
#                     return found
#         except Exception as e:
#             print(e)
    
#     return found

# print(check_programs("SDM IVI", r"SOFTWARE\Classes\.dmm", "EasyDMM-XFile.dmm"))

# # import os

# # # Directory path
# # dir_path = r"install_files\SDM 3k4k IVIDmm V2.5_EN"

# # # List all files in the directory
# # for filename in os.listdir(dir_path):
# #     file_path = os.path.join(dir_path, filename)
    
# #     # Check if it is a file (not a subdirectory)
# #     if os.path.isfile(file_path):
# #         os.remove(file_path)  # Remove the file
# #         print(f"Deleted file: {filename}")

# # os.rmdir(dir_path)  # Remove the directory


import sys

print(sys.argv)