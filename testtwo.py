import os
from instrument import *
# os.system("py test.py hi")

a = instrument_handle()
a.name("hi")

print(a.name)

