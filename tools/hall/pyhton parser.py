import csv 

i = 0
headers = []
datas = []
data = 0

def strip_space(str):
    
    
    no_space = []
    word = ""
    i = 0
    for char in str:
        
        if char  != " ":
            word += char
        else:
            if word != "":
                no_space.append(word)
            word = ""

        i += 1
    
    if word != "":
        no_space.append(word)
    
    
    return no_space

temp = []


with open("C-15222C_HEMS_Data.txt","r") as f:
    lines = f.readlines()
    for line in lines:
        if line.find("----") == -1 and line.find("===") == -1:
            temp = strip_space(line.strip())
            if temp != []:
                #dealing with non- numeric data
                if i == 0:
                    for obj in temp:headers.append(obj)
                if i == 1:
                    for obj in temp:datas.append(obj)
                else:
                    try:
                        data = float(temp[0])
                        for obj in temp:datas.append(obj)
                    except ValueError:
                        for obj in temp:headers.append(obj)

        i += 1
#22 to 31 need to be fixed 32 and 33 need to be removed


i = 22
plus = headers[32]
minus = headers[33]
last = headers[-1]
new = headers[:32]


for header in headers[22:32]:
    new.append(headers[i] + minus)
    new[i] =  headers[i] + plus
   
    i += 1

final = new.append(last)
stop = True